#!/bin/sh

if [ ! -f /var/flags/dbinit ]; then
  # Wait for db to come up
  ping -c 10 db > /dev/null || (echo "DB unreachable";exit)

  # Setup Couch DB single node instance
  # For more information see https://github.com/apache/couchdb-docker#no-system-databases-until-the-installation-is-finalized
  setup_dbs="_users _replicator _global_changes"
  echo "Setup DB with "${setup_dbs}
  python ./create_database.py ${setup_dbs}

  # Create databases
  dbs=$(grep -o "'.*'" ./server/entities/databases.py  | sed "s/'//g")
  echo "Creating databases "${dbs}
  python ./create_database.py ${dbs}
  
  # Set initialized
  echo "CouchDB initialized"
  touch /var/flags/dbinit
fi
