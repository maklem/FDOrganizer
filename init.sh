#!/bin/sh

if [ ! -f ./initialized ]; then
  # Wait for db to come up
  ping -c 10 db > /dev/null || (echo "DB unreachable";exit)
  
  # Create darabases
  dbs=$(grep -o "'.*'" ./server/entities/databases.py  | sed "s/'//g")
  echo "Creating databases "${dbs}
  python ./create_database.py ${dbs}
  
  # Set initialized
  echo "CouchDB initialized"
  touch ./initialized
fi

flask --app server --debug run --host=0.0.0.0 --cert=/server/server/ssl/ca.crt --key=/server/server/ssl/ca.key