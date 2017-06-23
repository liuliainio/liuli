#!/bin/bash
operator_file=$1
create_push_log=$2
if [ ! -f "$operator_file" ];then
    echo "usage error: $operator_file is not exits."
    exit 1
fi

LOG_FILES=()
LOG_PATH=/tmp
PARSE_TYPE='prod-cnet'
OUT_FILE_PART=`date -d'-1 day' +%Y%m%d`
OUT_FILE_NAME="operator_${OUT_FILE_PART}"

OUTPUT_TEMP=''

LOG_DIR=`date -d'-1 day' +%Y/%m`
LOG_FILE_PART=`date +%Y%m%d`

BASE_REPORTING_FILE='/www/site/game/game/private/reports/channel_reports'
REPORTING_FILE="${BASE_REPORTING_FILE}/${PARSE_TYPE}/operaotr.info"
SAVE_PATH="/var/app/data/raw/${PARSE_TYPE}/log"
PUSH_LOG_PATH="${SAVE_PATH}/service/${LOG_DIR}"
ACCESS_LOG_PATH="${SAVE_PATH}/service-webfront/${LOG_DIR}"

PUSH_LOG_FILES=("info.log-${LOG_FILE_PART}-182.140.141.43.gz"
               "info.log-${LOG_FILE_PART}-182.140.141.44.gz"
               "info.log-${LOG_FILE_PART}-182.140.141.120.gz"
               "info.log-${LOG_FILE_PART}-182.140.141.121.gz")

ACCESS_LOG_FILES=("access.log-${LOG_FILE_PART}-182.140.141.46.gz"
                  "access.log-${LOG_FILE_PART}-182.140.141.45.gz")

function make_channel_log()
{
    parse_type=$1
    loop_status=0
    #enter log dir
    pushd $LOG_PATH
    for file in ${LOG_FILES[*]}
        do
            if [ -f $file ];then
                run_parse $file $parse_type;
                sleep 1
            else
                echo "Error:$file is not exist."
                loop_status=1
                break
            fi
        done
    #leave log dir
    popd
    return $loop_status
}



function run_parse()
{
    file=$1
    parse_type=$2
    echo $file,$parse_type
    case $parse_type in
    'push')
        echo "zgrep -i '^INFO.*push_notification_messages' $file|sed 's/.*clientid=\([^,]*\).*imsi=|\([^,]*\).*/\1,\2/g' >> $OUTPUT_TEMP"
        exec_result=`zgrep -i '^INFO.*push_notification_messages' $file|sed 's/.*clientid=\([^,]*\).*imsi=|\([^,]*\).*/\1,\2/g' >> $OUTPUT_TEMP`
        #echo $exec_result
        ;;
    'access')
        echo "zgrep -E -i 'recommends\.json.*clientid=[^(zabbix)]' $file |sed 's/.*clientid=\([^&]*\).*/\1/g' >> $OUTPUT_TEMP"
        exec_result=`zgrep -E -i 'recommends\.json.*clientid=[^(zabbix)]' $file |sed 's/.*clientid=\([^&]*\).*/\1/g' >> $OUTPUT_TEMP`
        #echo $exec_result
        ;;
    *)
        echo 'setting type do not matched! please input right type, e.g. "push" or "access".'
        exit 1
        ;;
    esac
}


function check_file_exist()
{
    file=$1
    if [ $file -a -f $file ];then
        return 0
    else
        return 1
    fi
}



echo "create access tmp log"

if [ "$create_push_log" = "force" ];then
    #cerate push tmp log
    LOG_PATH=$PUSH_LOG_PATH
    LOG_FILES=${PUSH_LOG_FILES[*]}
    OUTPUT_TEMP="/tmp/push_$OUT_FILE_NAME.tmp"
    PUSH_TEMP="/tmp/push_$OUT_FILE_NAME.slim.tmp"
    check_file_exist $PUSH_TEMP
    ret=$?
    if [ $ret -eq 1 ];then
        make_channel_log 'push';
        sort_result=`sort -u $OUTPUT_TEMP > $PUSH_TEMP`
        echo $sort_result
        rm_result=`rm $OUTPUT_TEMP`
        echo $rm_result
    else
        echo "File $PUSH_TEMP exists."
        PUSH_TEMP=''
    fi
fi

#create access tmp log
LOG_PATH=$ACCESS_LOG_PATH
LOG_FILES=${ACCESS_LOG_FILES[*]}
OUTPUT_TEMP="/tmp/access_$OUT_FILE_NAME.tmp"
check_file_exist $OUTPUT_TEMP
ret=$?
if [ $ret -eq 1 ];then
    make_channel_log 'access';
else
    echo "Access File $OUTPUT_TEMP exists."
fi

run_script=`python operator_api_log.py $operator_file $OUTPUT_TEMP $PUSH_TEMP`
echo -e "$run_script" >> $REPORTING_FILE
