# Video Downloader server

In MediaHub 0.6.96 or later, open this app under **Apps** (**App Store** in 0.6.96), choose your storage folder on first install, and select Install or update. Updates use the same screen. [Dansk vejledning](video-downloader.da.md)

Install on a Linux Docker host with the Compose plugin. Prepare a writable downloads directory and a server certificate issued by your trusted CA. The installer can also issue the server certificate using a local CA certificate and signing key. Keep your CA key on its trusted host. For an already-issued certificate, put server.pem, server-key.pem and ca.pem in /opt/video-downloader/tls with permissions readable by the app user (default UID 1000).

Download fetch.py from the [package index](../README.md). As administrator, substitute your own HTTPS name, port, LAN IP and mounted download directory:

```sh
release=$(python3 fetch.py video-downloader --directory /opt/mediahub/app-packages) &&
  PUBLIC_ORIGIN=https://video.example.org:18810 BIND_ADDRESS=192.0.2.10 DOWNLOADS_DIR=/srv/downloads bash "$release/server/install.sh"
```

For first login, run `python3 "$release/server/setup-link.py" /opt/video-downloader` locally. The setup link is private and single use. To update, fetch the current release and run its server/install.sh again. The installer reuses the saved settings and download location. Finish active jobs before updating.
