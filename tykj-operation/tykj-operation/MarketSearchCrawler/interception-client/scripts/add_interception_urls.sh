#!/bin/bash

log_file=/var/app/log/download_interception/cron.log
mkdir -p `dirname $log_file`
chmod a+rw `dirname $log_file`
echo begin add interception urls at `date +"%Y%m%d %H:%M:%S"` >> $log_file
cd /var/app/enabled/download-interception/
tail -n2000 /var/app/log/service/openapi.log | grep 'dolphin_download with external' | python add_interception_urls.py >> $log_file 2>&1

