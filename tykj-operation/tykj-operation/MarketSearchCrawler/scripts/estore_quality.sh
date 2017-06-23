#!/bin/bash - 
#===============================================================================
#
#          FILE: estore_quality.sh
# 
#         USAGE: ./estore_quality.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: YOUR NAME (), 
#  ORGANIZATION: 
#       CREATED: 2013年11月22日 17时33分26秒 CST
#      REVISION:  ---
#===============================================================================



# should add line below to /etc/hosts first
# 192.168.130.109     estoresrvice.189store.com

oldpwd=`pwd`
this_file=$0
if [[ -h $0 ]];then
    this_file=`ls -l $0|awk -F"->" '{print $2}'`
fi
ws=`dirname $this_file`
cd $ws
ws=`pwd`


proj_dir=`dirname $(pwd)`
export PYTHONPATH=$proj_dir
export LANG=zh_CN.UTF-8
export LANGUAGE=zh_CN:zh

cat /tmp/estore_quality_kpi1.mail >> /tmp/estore_quality_kpi1.mail.log
cat /tmp/estore_quality_kpi2.mail >> /tmp/estore_quality_kpi2.mail.log
python "$proj_dir/services/kpi/__init__.py" > /tmp/estore_quality_kpi1.mail
python "$proj_dir/services/kpi/__init__.py" kpi2 > /tmp/estore_quality_kpi2.mail


mail_to=gmliao@bainainfo.com,jliang@bainainfo.com,lyliu@bainainfo.com,jjpan@bainainfo.com,jli@bainainfo.com,yyao@bainainfo.com
theme="estore quality - $(date +'%Y%m%d %H:%M:%S')"
cat /tmp/estore_quality_kpi1.mail | grep -v 'MainThread' | mail -s "$theme" $mail_to
cat /tmp/estore_quality_kpi2.mail | grep -v 'MainThread' | mail -s "$theme" $mail_to


cd $oldpwd
exit 0
