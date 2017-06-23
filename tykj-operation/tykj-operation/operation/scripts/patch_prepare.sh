#!/bin/bash
REMOTE_PATH=/home/gmliao/analysis/statistics/incremental_download/update_hasnewversionapps.data
SAVE_PATH=/var/app/data/patch_ids/
YEAR=$(date +"%Y")
MONTH=$(date +"%m")
DAY=$(date +"%d")
FULL_TIME=$YEAR$MONTH$DAY
REMOTE_FILE=/${YEAR}/${MONTH}/${FULL_TIME}.out
FULL_FILE_PATH="${REMOTE_PATH}${REMOTE_FILE}"
SCP_REMOTE_FILE="scp -C jjpan@221.236.24.18:${FULL_FILE_PATH} ${SAVE_PATH}"
SAVE_FILE="${SAVE_PATH}${FULL_TIME}.out"

if [ ! -d $SAVE_PATH ]; then
    echo "patch logs目录不存在."
    mkdir $SAVE_PATH
    if [ $? -ne 0 ];then
    echo "创建目录失败，退出！"
    exit 1
    else
    chmod -R 777 $SAVE_PATH
    echo "创建目录$SAVE_PATH"
    fi
fi
if [ ! -f $SAVE_FILE ]; then
    echo "Save Path目录存在,准备拷贝文件."
    echo $SCP_REMOTE_FILE
    $SCP_REMOTE_FILE
    ret=$?
    if [ $ret -ne 0 ];then
        echo "远程Copy文件失败，返回码：$ret"
        exit 1
    else
        echo "文件拷贝完毕."
    fi
else
    echo "远程文件已存在."
fi
cd /var/app/enabled/operation/estoreoperation
echo "Patch File:"$SAVE_FILE
python manage.py api_log_patch "$SAVE_FILE" >> /tmp/api_log_patch.log 2>&1
