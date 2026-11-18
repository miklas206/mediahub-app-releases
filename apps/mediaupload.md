# MediaUpload

Install the standalone Docker edition on a Linux host with Python 3, OpenSSL, Docker and its Compose plugin. Choose a readable media library. MediaUpload mounts it read-only. Prepared copies and persistent settings live under /opt/mediaupload-docker.

Download fetch.py from the [package index](../README.md). Run as administrator:

```sh
release=$(python3 fetch.py mediaupload --directory /opt/mediahub/app-packages) &&
  python3 "$release/install.py" --library /srv/media --origin https://upload.example.org:18820 --bind 192.0.2.10
```

Substitute your own DNS name, local address and library. Open the configured HTTPS address. The login is admin and the generated password is in /opt/mediaupload-docker/initial-password on the host. Provide your trusted certificate and key as tls/server.pem and tls/server-key.pem in that directory, or trust the generated certificate after checking its fingerprint on the host. Tracker and metadata credentials belong to your installation. If you have the tracker’s rules, put nordicbytes-upload.txt, nordicbytes-general.txt and nordicbytes-faq.txt in the rules directory.

For Docker updates, fetch the current package and rerun its install.py. It reuses settings, credentials, queued jobs and media. Existing gateway-managed systemd deployments retain their own unit and gateway configuration. For those deployments, take a database/configuration backup, wait for active preparation to finish, then update the installed Python package in its existing virtual environment and restart its two services.
