"""Publish an allowlisted server package from a clean, tagged private source checkout."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import tarfile
import tempfile
from urllib.request import urlopen

CHANNEL = Path(__file__).resolve().parent
OWNER = "miklas206"
PUBLIC = OWNER + "/mediahub-app-releases"


def cmd(*args, cwd):
    return subprocess.check_output(args, cwd=cwd)


def publish(app, repo):
    def source(*args):
        return cmd("git", *args, cwd=repo)
    private = OWNER + "/" + app
    if not json.loads(cmd("gh", "api", "repos/" + private, cwd=repo))["private"]:
        raise ValueError("The source repository must be private")
    if source("status", "--porcelain") or cmd("git", "status", "--porcelain",cwd=CHANNEL):
        raise ValueError("Commit the source and channel working trees first")
    commit = source("rev-parse", "HEAD").decode().strip()
    version = source("show", commit + ":VERSION").decode().strip()
    if not re.fullmatch(r"(0|[1-9][0-9]*)(\.(0|[1-9][0-9]*)){2}", version):
        raise ValueError("Expected a three-part version")
    remote_commit = cmd("gh","api","repos/"+private+"/commits/v"+version,"--jq",".sha",cwd=repo).decode().strip()
    if remote_commit != commit:
        raise ValueError("Push the source tag v" + version + " before publishing")
    index = CHANNEL / "apps" / (app + ".json")
    if index.exists() and tuple(map(int, json.loads(index.read_text())["version"].split("."))) >= tuple(map(int,version.split("."))):
        raise ValueError("Choose a version newer than the published package")
    tag = f"{app}-v{version}"
    with tempfile.TemporaryDirectory() as work:
        archive = Path(work) / (tag + ".tar.gz")
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w", format=tarfile.USTAR_FORMAT) as tar:
            names = source("show", commit + ":package-files.txt").decode().splitlines()
            if len(set(names)) != len(names) or not {"VERSION","README.md"} <= set(names):
                raise ValueError("Invalid package file list")
            for name in names:
                if not all(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_. -]*",part) for part in name.split("/")):
                    raise ValueError("Invalid package file name")
                content=source("show", commit+":"+name)
                entry=tarfile.TarInfo(name)
                entry.mode=0o755 if name.endswith(".sh") else 0o644
                entry.size=len(content)
                tar.addfile(entry,io.BytesIO(content))
        archive.write_bytes(gzip.compress(buffer.getvalue(),mtime=0))
        digest=hashlib.sha256(archive.read_bytes()).hexdigest()
        checksum=Path(work)/(tag+".sha256")
        checksum.write_text(f"{digest}  {archive.name}\n")
        # A retry after publishing assets can finish the index without replacing assets.
        release_exists = subprocess.run(["gh","release","view",tag,"-R",PUBLIC],capture_output=True).returncode==0
        if not release_exists:
            cmd("gh","release","create",tag,str(archive),str(checksum),"-R",PUBLIC,"--latest=false","--target","main",
                "--title",f"{app} {version}","--notes",f"Verified server package. SHA-256 {digest}",cwd=CHANNEL)
        with urlopen(f"https://github.com/{PUBLIC}/releases/download/{tag}/{archive.name}",timeout=60) as downloaded:
            if hashlib.sha256(downloaded.read(32*1024*1024+1)).hexdigest()!=digest:
                raise ValueError("Public release differs from the tagged source")
    index.write_text(json.dumps(dict(app=app,version=version,sha256=digest,sourceCommit=commit),indent=2)+"\n")
    cmd("git","add","--",str(index),cwd=CHANNEL)
    cmd("git","commit","-m",f"Publish {app} {version}",cwd=CHANNEL)
    cmd("git","push","origin","HEAD:main",cwd=CHANNEL)


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("app",choices=["mediaupload","video-downloader","plex-gpu-transcoder"])
    parser.add_argument("source",type=Path)
    args=parser.parse_args()
    publish(args.app,args.source.resolve(strict=True))
