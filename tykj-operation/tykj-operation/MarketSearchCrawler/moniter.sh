#!/bin/bash

while [ 1 -eq 1 ];do
    date
    if [[ $1 == 'update.wandoujia.com' ]];then
        (sudo bash -c "export http_proxy=http://192.168.130.77:3128 && scrapy crawl $1 --logfile=/tmp/spider_$1.log")
    else    
        sudo scrapy crawl $1 --logfile=/tmp/spider_$1.log
    fi
done
