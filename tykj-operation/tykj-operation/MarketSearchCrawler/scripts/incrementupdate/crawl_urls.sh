#!/bin/bash - 
#===============================================================================
#
#          FILE: crawl_urls.sh
# 
#         USAGE: ./crawl_urls.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: YOUR NAME (), 
#  ORGANIZATION: 
#       CREATED: 2014年02月22日 15时06分01秒 CST
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error

while [[ 1 == 1 ]]; do
    sudo bash -c 'cd /var/app/enabled/MarketSearchCrawler && scrapy crawl downloadlink.as.baidu.com --logfile=/tmp/spider_downloadlink.as.baidu.com.log'
    sleep 600
done



