#!/bin/bash - 
#===============================================================================
#
#          FILE: monitor_baidu.sh
# 
#         USAGE: ./monitor_baidu.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: YOUR NAME (), 
#  ORGANIZATION: 
#       CREATED: 2013年09月07日 17时21分37秒 CST
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error

max_stop_sec=30

function stop_spider()
{
local src=$1
local stop_sec=$2
tail -n100 /tmp/spider_update.$src.log | grep '+0800' | tail -n1 | sed 's/\(.*\)+0800.*/\1/g' | xargs -I {} date -d'{}' +%s | \
    while read _d;do \
        _cd=$(($(date +%s) - $_d)); \
        if [[ $_cd -gt $stop_sec ]]; then \
            echo $_d greater than $stop_sec, kill spider; \
            (ps aux | grep $src | grep -v bash| grep -v grep | grep -v tail | awk '{print $2}' | xargs sudo kill -9); \
        else \
            echo passed spider $src for stop_sec $stop_sec; \
        fi; \
    done
}


stop_spider as.baidu.com 30
stop_spider wandoujia.com 30
stop_spider zhushou.360.cn 30
