if [ -f ../.env ]; then
  export $(echo $(cat ../.env | sed 's/#.*//g'| xargs) | envsubst)
fi

docker exec $MYSQL /usr/bin/mysqldump -uroot --password=$MYSQL_PASSWORD $MYSQL_DATABASE >  backup/$(date '+%Y-%m-%d_%H:%M:%S').sql
