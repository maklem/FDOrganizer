if [ ! -f /var/flags/orginit ]; then
  python ./create_organisation.py "dummy_organisation.json"
  touch /var/flags/orginit
fi
