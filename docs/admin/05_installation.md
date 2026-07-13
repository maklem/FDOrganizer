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

# Configure expiry of documents
FDO_KEEP_ACTIVE_PACKAGES_DAYS=60
FDO_KEEP_ARCHIVED_PACKAGES_DAYS=15
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

You will learn later how to [configure FDO](20_user_access.md) for your needs.
For now we only need a valid database setup without contents.


## run FDOrganizer as a service

FDOrganizer supplies `uwsgi.ini` to run a production server. Depending on your
setup it might need some adjustments.

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
socket-timeout = 300

vacuum = true

die-on-term = true
```

To run FDO as a system service we will use a script `/srv/fdorganizer/start-fdo-as-service.bash`

```bash, /srv/fdorganizer/start-fdo-as-service.bash
#!/bin/bash

source $HOME/venv/bin/activate
uwsgi --ini uwsgi.ini
```

and create a systemd service in `/etc/systemd/system/fdo.service`

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

After creation of the service and script, FDOrganizer can be started using

```bash
sudo systemctl daemon-reload
sudo systemctl start fdo
```

## nginx configuration

So far we have FDOrganizer running as a system service, and serving pages via
uwsgi on a local file socket. To make it accessible for browsers we will use
nginx as reverse proxy.

A minimal configuration could look like

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

        uwsgi_read_timeout 300s;
        uwsgi_send_timeout 300s;
    }

    listen [::]:443 ssl ipv6only=on; # managed by Certbot
    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/domain.example/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/domain.example/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
}
```
We can store the configuration as `/etc/nginx/sites-available/fdorganizer.conf`.

It can be made active using
```sh
sudo ln -s /etc/nginx/sites-available/fdorganizer.conf /etc/nginx/sites-enabled/
```

Next, we test the validity of our configuration
```sh
sudo nginx -t
```

If the test passes, we restart nginx to load the new configuration
```sh
sudo systemctl restart nginx
```

Note:
* If you have no TLS/SSL certificate yet, why don't you get one using certbot?
  In case your server is not accessible from the internet (and thus can not be
  domain validated) you may remove/adjust the lines referring to *ssl*.
* Request can be blocked on many layers.
  Here the line `client_max_body_size 1G;` expands the limits of uploads to 1GB (default in nginx is 1MB).
  Any larger request will be blocked by nginx, and not reach FDO.

