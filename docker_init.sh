#!/bin/sh

TRACER=/var/flags/fdo-docker-init

echo "=== INIT DOCKER ==="
echo "COUCHDB_HOST = $COUCHDB_HOST"
echo "COUCHDB_PORT = $COUCHDB_PORT"
echo "COUCHDB_USER = $COUCHDB_USER"

sleep 5;
echo "=== initializing ==="

python3 -u maintenance.py databases
if [ ! -f $TRACER ]; then
    echo "=== dummy organisation ==="
    python3 -u maintenance.py populate organisations dummy_organisation.json
    echo "=== dummy keycloak idp ==="
    python3 -u maintenance.py populate identityproviders dummy_keycloak_idp.json
    echo "=== dummy local idp ==="
    python3 -u maintenance.py populate identityproviders dummy_local_idp.json
    echo "=== dummy local users ==="
    python3 -u maintenance.py populate users dummy_local_users.json
    mkdir -p /var/flags
    touch $TRACER
fi
echo "=== done. ==="