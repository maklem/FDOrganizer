if [ ! -f /server/organized ]; then
  python ./create_organisation.py "dummy_organisation.json"
  touch /server/organized
fi
