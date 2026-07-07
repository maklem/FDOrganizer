# Enabling Administrative Access

FDOrganizer does not have an administriative interface built into the software.
Instead administrators need to apply changes the database directly.

CouchDB (the database software used by FDOrganizer) ships with an administrative UI named Fauxton.
It runs on `http://couchdb-host:5984/_utils/`. However CouchDB listens to localhost only, and it is good to keep it that way.
There are many ways to still gain access to the database. Here I outline one I consider pactical.

Then you need administrative user accounts, to log into the database. Instructions follow below.

## Reverse Proxy Configuration: nginx

If nginx is already in use to proxy FDOrganizer, and serves as HTTPS termination,
adding an additional reverse proxy is quite easy.

I.e. add a new server configuration as `/etc/nginx/sites-available/forward-fdo-couchdb.conf`.
```conf
server {
    # Set up listening adresses
    # 
    # Note: 
    # 127.0.0.1:5984 is already in use by couchdb.
    # To avoid confict, nginx can listen on specific ip-addresses only, or on a different port.
    listen 5980 ssl;
    listen [::]:5980 ssl ipv6only=on;

    # HTTPS Configuration
    # Use Certbot
    ssl_certificate /etc/letsencrypt/live/domain.example/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/domain.example/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location / {
            proxy_pass http://127.0.0.1:5984;
            proxy_set_header Host $http_host;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header X-Forwarded-Host $host;
            proxy_set_header X-Forwarded-Port $server_port;
    }
}
```
Here we are reusing the certificate obtained for the FDOrganizer instance.

## CouchDB users

For couchdb, admin accounts are specified in configuration files.
Installed from Apache's APT repositories, all configuration files
are in `/opt/couchdb/etc/`

In `local.d/10-admins.ini` you can add and remove admins. You may add users
here with passwords in plaintext.
```ini
[admins]
myuser = ntpTB5Z8WXSjEqsWBS7k
```
When CouchDB is restarted next time, users are reloaded, and passwords
are replaced by hashes. 
```ini
[admins]
myuser = -pbkdf2:sha256-962435e85d2476f7ec3c0a7aa1e82614b15c9c115e7338c35e4fa755edfb58db,730256ceb32d97fedcc2a75b2967b629,600000
```
You can remove admins, by removing a line, or marking it as a comment (a lines starting with `#` or `;`).

**Note:** Technically admins can be added in `local.ini` as well. However
these have passwords kept in plaintext. Contrary to the description, the
password is not replaced here. Instead they are added (with hashed password)
to `local.d/10-admins.ini`.

## Security Hardening

IP based filters are considered weak. Still they add a tiny bit of security,
and reduce load on backend systems caused by web crawlers.

Two way TLS is much stronger in terms of security, but require good handling
of client certificates, and add complexity and load on administrators.

### ip based filter - iptables

`iptables` is a strong firewall present in most recent linux distributions.
As it operates on network level, it can be used to block (DROP or REJECT)
connections to+from any client.

```sh
iptables -A INPUT -s 10.200.0.0/16 -p tcp --port 5980 -j ACCEPT
iptables -A INPUT -p tcp --port 5980 -j DROP
```

**Important:** 
* Make sure, that you explicitly allow your SSH connection! 
  You will not be able to do that, once you block that connection.
* Lines are parsed top to bottom. The first line that matches wins.
  Thus the line that drops *any other* connection should be the last line.

### ip based filter - nginx

When using nginx to filter connections, you will always get a full HTTPS+HTML response.
It's easier to debug (you can check the logs in `/var/log/nginx/access.log`) and are unlikely
to interfere with other systems.

In you virtual server configuration, you add lines like:
```conf
server {
    # ...

    # Security Hardening - Option B: ip address restriction in nginx
    allow 10.200.0.0/16; # Allow FAU internal
    deny all;            # Deny everyone else

    # ...
}
```

### Client Certificates

Nginx, as well as other web servers, can be configured to require a client to authenticate with a TLS certificate,
like in HTTPS the server is authenticated with a certificate. 

You can become a certificate authority, and issue certificates for your administrators (i.e. using easy-rsa).
But be aware that this increases load on your technical staff, and can easily lock you out from managing 
your FDOrganizer instance.

**Only use client certificates, when you know what you are doing.**

As a starting point, this configuration requires clients to authenticate using a certificate signed by
a local CA stored in `/etc/nginx/pki/`.
```conf
server {
    # ...

    ssl_client_certificate /etc/nginx/pki/ca.crt;
    ssl_crl /etc/nginx/pki/crl.pem;
    ssl_verify_client  on;

    # ...
}
```
