#!/bin/bash -
#===============================================================================
#
#          FILE: find_beta_apps.sh
#
#         USAGE: ./find_beta_apps.sh
#
#   DESCRIPTION:
#
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: YOUR NAME (),
#  ORGANIZATION:
#       CREATED: 12/19/2013 12:09:47 PM CST
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


mail_to=jliang@bainainfo.com,gmliao@bainainfo.com,jjpan@bainainfo.com,jli@bainainfo.com,lyliu@bainainfo.com,xhhu@bainainfo.com
. ../env.sh
test -f /tmp/find_beta_apps.mail && cat /tmp/find_beta_apps.mail >> /tmp/find_beta_apps.mail.log
sql="set character_set_client=utf8;set character_set_connection=utf8;set character_set_results=utf8;select name, package_name , version, version_code , source, created_at from final_app where date(created_at) = date_sub(curdate(), interval 1 day) and (name like '%beta%' or name like '%体验版%' or name like '%测试版%');"
theme="Beta Version App Report -- `date -d'-1 day' +%Y-%m-%d %H:%M:%S`"
$mysql_conn -e "$sql" > /tmp/find_beta_apps.mail

cat /tmp/find_beta_apps.mail | mail -s "$theme" $mail_to

cd $oldpwd
exit 0
