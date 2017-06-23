#!/bin/bash - 
#===============================================================================
#
#          FILE: add_verification_ids_update.sh
# 
#         USAGE: ./add_verification_ids_update.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: YOUR NAME (), 
#  ORGANIZATION: 
#       CREATED: 2013年09月25日 14时48分26秒 CST
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error


log_file=/var/app/log/MarketSearchCrawler/add_verfication_ids_update.log


function main(){
    maxid1=$(mysql -udev_market -pmarket_dev_pwd -h192.168.130.77 market -e 'select max(final_app_id) from final_app_safe\G' | grep max | sed 's/max.*: *\([0-9]*\)$/\1/g')
    maxid2=$(mysql -udev_market -pmarket_dev_pwd -h192.168.130.77 market -e 'select max(id) from final_app\G' | grep max | sed 's/max.*: *\([0-9]*\)$/\1/g')

    echo will add id from $maxid1 to $maxid2 to rabbitmq

    ids=$(python -c "print ','.join([str(s) for s in range($maxid1, $maxid2 + 1)])")
    cd /var/app/enabled/MarketSearchCrawler/
    export PYTHONPATH=/var/app/enabled/MarketSearchCrawler/
    echo python services/verification/add_verification_ids.py ids=$ids
    python services/verification/add_verification_ids.py ids=$ids

}

mkdir -p `dirname $log_file`
main >> $log_file 2>&1

