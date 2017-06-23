#!/bin/bash - 
#===============================================================================
#
#          FILE: merge_meta.sh
# 
#         USAGE: ./merge_meta.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: YOUR NAME (), 
#  ORGANIZATION: 
#       CREATED: 2013年08月23日 19时36分52秒 CST
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

. env.sh

num_apps=100000

id_to=$($mysql_conn -e "select id from final_app order by id desc limit $num_apps,1\G" | grep 'id:' | cut -d':' -f2 | tr -d ' ')

id_from=$(mysql_conn -e 'select max(id) from final_app\G' | grep 'max(id):' | cut -d':' -f2 | tr -d ' ')

echo will merge app meta info from id=$id_to to id=$id_from

echo start at: `date`

python /var/app/enabled/MarketSearchCrawler/merge_meta.py count=1000 id_from=$id_from id_to=$id_to >> /tmp/merge_meta_update.log 2>&1

echo end at: `date`
