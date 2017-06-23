#!/bin/bash - 
#===============================================================================
#
#          FILE: start-service.sh
# 
#         USAGE: ./start-service.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: YOUR NAME (), 
#  ORGANIZATION: 
#       CREATED: 2013年09月05日 11时45分08秒 CST
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

sudo bash -c '\
export PYTHONPATH=/usr/lib/python2.6/site-packages && \
cd ../src && \
python apkpatch_server.py >> /tmp/spider_apkpatch_service.log 2>&1\
'

cd $oldpwd
exit 0

