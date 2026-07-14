# Maintenance

## Configuration

In [installation](05_installation.md) you might have noticed the 
document expiry configuration in `.env`.

```ini
# Configure expiry of documents
FDO_KEEP_ACTIVE_PACKAGES_DAYS=60
FDO_KEEP_ARCHIVED_PACKAGES_DAYS=15
```
These configure, how long a package should be kept, after its status
changed to an active category (active, review, needs rework), and 
the final archived category. Expired documents are not deleted here yet.

## Manual Deletion

To scan the database for expired documents and delete them, run
```sh
python3 cron_deleter.py
```

CouchDB keeps "tombstone documents" to share deletion of documents in distributed databases.
For FDO we have a single database, and can delete these. To do that run
```sh
python3 cron_purge_tombstones.py
```

## Automated Deletion

Previous maintenance tasks can be automated using a script.
```bash
#!/bin/bash

mkdir -p /srv/fdorganizer/cron/log/

cd /srv/fdorganizer/FDOrganizer/

/srv/fdorganizer/venv/bin/python3 /srv/fdorganizer/FDOrganizer/cron_deleter.py > /srv/fdorganizer/cron/log/$(date --iso).log
/srv/fdorganizer/venv/bin/python3 /srv/fdorganizer/FDOrganizer/cron_purge_tombstones.py >> /srv/fdorganizer/cron/log/$(date --iso).log

source /srv/fdorganizer/FDOrganizer/.env
COUCHDB=http://$COUCHDB_USER:$COUCHDB_PASSWORD@$COUCHDB_HOST:$COUCHDB_PORT

curl -H "Content-Type: application/json" -X POST $COUCHDB/packages/_compact > /dev/null
curl -H "Content-Type: application/json" -X POST $COUCHDB/documents/_compact > /dev/null
curl -H "Content-Type: application/json" -X POST $COUCHDB/folders/_compact > /dev/null
```

If stored as `/srv/fdorganizer/cron/delete-daily.sh` it can configured for
daily execution using `crontab -e`. There add a new line:
```crontab
0 4 * * * /srv/fdorganizer/cron/delete-daily.sh > /dev/null
```