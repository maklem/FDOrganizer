# Installation

## CouchDB Installation

Follow the instructions from CouchDB for your platform: https://docs.couchdb.org/en/stable/install/index.html

## System User for FDOrganizer

```sh
sudo adduser --system fdorganizer --home /srv/fdorganizer --ingroup www-data
```

## Git Source Code

Log into fdorganizer user
```sh
sudo -u fdorganizer bash
cd $HOME
```

Clone the code from a git hoster of your choice (GitHub, RRZE-Gitos, ...)
```sh
git clone git@gitos.rrze.fau.de:on95evoc/fdorganizer.git
```

## Virtual Env

set up the virtual environment
```sh
cd $HOME
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## configure FDOrganizer

FDOrganizer is configured using a `.env` file. You will need your couchdb credentials.

Additionally generate a `TOKEN_SECRET` using a source of random data, i.e. `openssl rand -base64 64`. (This secret is used to sign+validate authentication cookies.)

```sh, .env
COUCHDB_USER=...
COUCHDB_PASSWORD=...
COUCHDB_HOST=127.0.0.1
COUCHDB_PORT=5984
# EXPORT_DIR=/srv/fdorganizer/exported/
# EXPORT_USER=110 # uid of fdorganizer
# IMPRESSUM_LINK=https://localhost:5000/impressum
TOKEN_SECRET=...
```

If you plan to have data stored on disk, specify `EXPORT_DIR` and `EXPORT_USER`.

For production servers add a link to your legal imprint.

## Prepare the database

```sh
python maintenance.py databases
```

**For testing and development only** you may populate the database with preconfigured entities.
```sh
python maintenance.py populate organisations dummy_organisation.json
python maintenance.py populate identityproviders dummy_local_idp.json
python maintenance.py populate users dummy_local_users.json
```

See [configuring FDO](20_config.md) on how to configure FDOrganizer for your needs.

## run FDOrganizer as a service

```ini, uwsgi.ini
[uwsgi]
wsgi-file = wsgi.py
callable = APP

master = true
processes = 10

socket= /tmp/fdo-uwsgi.socket
http = 0.0.0.0:8080
http-to = /tmp/fdo-uwsgi.socket

chmod-socket = 666

vacuum = true

die-on-term = true
```

```bash, /srv/fdorganizer/start-fdo-as-service.bash
#!/bin/bash

source $HOME/venv/bin/activate
uwsgi --ini uwsgi.ini
```

```ini, /etc/systemd/system/fdo.service
[Unit]
Description=FDOrganizer uWSGI running as system service

[Service]
ExecStart=bash /srv/fdorganizer/start-fdo-as-service.bash
User=fdorganizer
Group=www-data
WorkingDirectory=/srv/fdorganizer/FDOrganizer/

[Install]
WantedBy=multi-user.target
```

## nginx configuration

```conf
server {
    root /var/www/html;
    server_name fdo-test.ub.uni-erlangen.de; # managed by Certbot

    client_max_body_size 1G;

    location / {
        uwsgi_pass unix:/tmp/fdo-uwsgi.socket;
        include uwsgi_params;
        uwsgi_param Host $host;
        uwsgi_param X-Real-IP $remote_addr;
        uwsgi_param X-Forwarded-For $proxy_add_x_forwarded_for;
        uwsgi_param X-Forwarded-Proto $http_x_forwarded_proto;
    }

    listen [::]:443 ssl ipv6only=on; # managed by Certbot
    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/domain.example/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/domain.example/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
}
```

Note:
* Request can be blocked on many layers.
  Here the line `client_max_body_size 1G;` expands the limits of uploads to 1GB (default in nginx is 1MB).
  Any larger request will be blocked by nginx, and not reach FDO.

