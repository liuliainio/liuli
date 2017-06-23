#!/bin/bash

while [ 1 -eq 1 ];do
    date
    mysql -uroot -pP@55word -hlocalhost market -e "update new_link set last_crawl=1 , priority=6 where source='$1' and (last_crawl=2 or priority=12)"
    sudo scrapy crawl $1
    sleep 1500    
done
