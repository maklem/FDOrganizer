sys_dbs='_user _replicator _global_changes'
data_dbs='documents packages metadata folders'

for i in $data_dbs; do
    echo "Resetting db: $i"
    python /usr/local/reset_database.py $i
done

for i in $sys_dbs; do
    echo "Resetting db: $i"
    python /usr/local/reset_database.py $i
done