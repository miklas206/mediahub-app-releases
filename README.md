# MediaHub app packages

Download the server edition of each app without a GitHub account. Each release page includes the package and its SHA-256 digest. The per-app index points to the current version.

| Application | Install and update |
| --- | --- |
| MediaUpload | [MediaUpload guide](apps/mediaupload.md) |
| Video Downloader | [Video Downloader server guide](apps/video-downloader.md) |
| Plex GPU Transcoder | [Plex extension guide](apps/plex-gpu-transcoder.md) |

For a standalone installation, use Python 3 and OpenSSL on the target Linux host. Download the release helper once and choose an app.

```sh
curl -fLSs https://raw.githubusercontent.com/miklas206/mediahub-app-releases/main/fetch.py -o fetch.py
python3 fetch.py mediaupload
```

The helper verifies the current archive and prints the path to its unpacked release. Follow the app guide to activate it. Repeat these steps for updates. Keep application data outside the versioned release directories.

## Publishing an update

The maintainer reviews package-files.txt in the private application repository, updates VERSION and runs the app’s tests. Push the reviewed source and its vX.Y.Z tag. From a current clean checkout of this distribution repository, run `python3 publish.py APP /path/to/private/checkout --signing-key /secure/path/to/publisher-key.pem` using the maintainer’s GitHub CLI login. The command builds only the listed files, checks the public download and advances that app’s index. The source repositories and their history stay private. The publisher signs each index with its Ed25519 key. The Hub checks the signature, its qualified minimum version and the declared Hub compatibility before installing a newer release.
