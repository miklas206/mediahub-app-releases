# Plex GPU Transcoder

This optional extension requires an installed MediaHub-managed Plex server and a prepared NVIDIA GPU on its Docker host. Install Plex from the MediaHub store first. The extension reads the required Plex libraries from your installed Plex image. Wait for active playback to finish.

Download fetch.py as described in the [package index](../README.md), then run on the Plex host as administrator:

```sh
release=$(python3 fetch.py plex-gpu-transcoder --directory /opt/mediahub/app-packages) &&
  python3 "$release/install.py"
```

Use the same command for updates. View status under Plex → Plex extensions. To restore the original Plex transcoder, run the same installer with `--disable`. Your media and sidecar data are retained. The extension includes components by qlerup from Fjord Remote Plex GPU Transcoder, distributed with permission.
