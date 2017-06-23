#!/bin/bash


oldpwd=`pwd`
this_file=$0
if [[ -h $0 ]];then
    this_file=`ls -l $0|awk -F"->" '{print $2}'`
fi
ws=`dirname $this_file`
cd $ws
ws=`pwd`


. env.sh

echo start update monitor

echo "update_link db status (priority: 6, new; 9-10, success; 11, fail; 12 missing):"
$mysql_conn -e 'select source, floor(priority), count(*) from update_link group by source, floor(priority);'


pid=$(ps aux|grep update.|grep -v update_moniter|grep -v 'tail -f'|grep -v 'grep'|grep -v update_meta|awk '{print $2}')
ps aux | egrep "(scrapy crawl update.)|( moniter.sh)"
pid=$(ps aux | egrep "(scrapy crawl update.)|( moniter.sh)" | awk '{print $2}')
echo $pid
for s_pid in $pid;do
    sudo kill -9 $s_pid
done
if [[ $mode == 'ct' ]]; then
    nohup /bin/bash moniter.sh update.as.baidu.com &
    nohup /bin/bash moniter.sh update.zhushou.360.cn &
    #nohup /bin/bash moniter.sh update.goapk.com &
    nohup /bin/bash moniter.sh update.hiapk.com &
    nohup /bin/bash moniter.sh update.wandoujia.com &
    nohup /bin/bash moniter.sh update.appchina.com &
    nohup /bin/bash moniter.sh update.myapp.com &
elif [[ $mode == 'diandian-international' ]]; then
    nohup /bin/bash moniter.sh 1mobile.com &
fi



echo clean update_link
python scripts/update_link_seed.py
