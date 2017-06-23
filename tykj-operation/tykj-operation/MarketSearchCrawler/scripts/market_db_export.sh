#!/bin/sh
SQL_FILE=market_`date +%Y%m%d`

echo "stop slave"
mysql -uroot -p'p@ssw0rd&mysql!' -e "slave stop;"

echo "start backing up market db (tables: app and link)"
mysqldump -uroot -p'p@ssw0rd&mysql!' --opt market app link > ~/backup/${SQL_FILE}.sql

echo "start slave"
mysql -uroot -p'p@ssw0rd&mysql!' -e "slave start;"

cd ~/backup
tar -czf ${SQL_FILE}.tar.gz ${SQL_FILE}.sql && rm ${SQL_FILE}.sql
echo "backup file at: ${SQL_FILE}.tar.gz"