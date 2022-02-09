if [ -f ../.env ]; then
  export $(echo $(cat ../.env | sed 's/#.*//g'| xargs) | envsubst)
fi

cat ./backup/20220209.sql | docker exec -i $MYSQL /usr/bin/mysql -uroot --password=$MYSQL_PASSWORD backup_db
