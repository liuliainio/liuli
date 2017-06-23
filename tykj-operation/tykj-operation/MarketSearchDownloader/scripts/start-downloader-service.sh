#!/bin/bash - 
#===============================================================================
#
#          FILE: start-downloader-service.sh
# 
#         USAGE: ./start-downloader-service.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: YOUR NAME (), 
#  ORGANIZATION: 
#       CREATED: 2013年12月14日 11时39分52秒 CST
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error
oldpwd=`pwd`
this_file=$0
if [[ -h $0 ]];then
    this_file=`ls -l $0|awk -F"->" '{print $2}'`
fi
ws=`dirname $this_file`
cd $ws
ws=`pwd`

mkdir -p /var/app/log/MarketSearchDownloader
chmod a+rw /var/app/log/MarketSearchDownloader

cd ..
./src/MarketSearch/download.sh 1mobile.com &
#./src/MarketSearch/download.sh as.baidu.com &
#./src/MarketSearch/download.sh wandoujia.com &
#./src/MarketSearch/download.sh appchina.com &
#./src/MarketSearch/download.sh myapp.com &

cd $oldpwd
exit 0



