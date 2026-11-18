#!/usr/bin/env python3
"""Download and verify one published MediaHub app into a versioned directory."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import tarfile
import tempfile
import urllib.request

PROJECT = "miklas206/mediahub-app-releases"
APPS = ("mediaupload", "video-downloader", "plex-gpu-transcoder")
LIMIT = 32 * 1024 * 1024


def fetch(url, limit):
    with urllib.request.urlopen(url, timeout=45) as response:
        if not response.geturl().startswith("https://"):
            raise ValueError("HTTPS required")
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError("Download exceeds its size limit")
    return data


def retrieve(app, destination):
    manifest = json.loads(fetch(f"https://raw.githubusercontent.com/{PROJECT}/main/apps/{app}.json", 16384))
    version = manifest["version"]
    if manifest["app"] != app or not re.fullmatch(r"(0|[1-9][0-9]*)(\.(0|[1-9][0-9]*)){2}", version):
        raise ValueError("Unexpected application or version")
    tag = f"{app}-v{version}"
    data = fetch(f"https://github.com/{PROJECT}/releases/download/{tag}/{tag}.tar.gz", LIMIT)
    digest = hashlib.sha256(data).hexdigest()
    if digest != manifest["sha256"]:
        raise ValueError("Release checksum mismatch")
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / tag
    stage = Path(tempfile.mkdtemp(prefix=".download-", dir=destination))
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
            seen = set()
            size = 0
            for member in archive:
                parts = member.name.split("/")
                if (not member.isfile() or any(p in ("", ".", "..") for p in parts)
                        or member.name in seen or len(seen) >= 2048):
                    raise ValueError("Unexpected file in package")
                seen.add(member.name)
                size += member.size
                if size > LIMIT:
                    raise ValueError("Unpacked package exceeds its size limit")
                path = stage.joinpath(*parts)
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open("xb") as output:
                    shutil.copyfileobj(archive.extractfile(member), output)
                path.chmod(0o755 if member.mode & 0o111 else 0o644)
        if not (stage / "README.md").is_file():
            raise ValueError("Missing installation instructions")
        if target.exists():
            # Confirm the entire existing release before reusing it on retry.
            entries = list(target.rglob("*"))
            if (target.is_symlink() or any(p.is_symlink() for p in entries)
                    or {p.relative_to(target).as_posix() for p in entries if p.is_file()} != seen
                    or any((target / name).read_bytes() != (stage / name).read_bytes() for name in seen)):
                raise ValueError(f"Existing release directory has local changes: {target}")
        else:
            stage.chmod(0o755)
            os.rename(stage, target)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("app", choices=APPS)
    parser.add_argument("--directory", type=Path, default=Path("mediahub-releases"))
    args = parser.parse_args()
    print(retrieve(args.app, args.directory).resolve())
