#!/bin/bash - 
#===============================================================================
#
#          FILE: verification_delete_files.sh
# 
#         USAGE: ./verification_delete_files.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: YOUR NAME (), 
#  ORGANIZATION: 
#       CREATED: 09/25/13 20:58:53 CST
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

. ../env.sh
MYSQL_CONN=$mysql_conn

function app_count()
{
    echo $($MYSQL_CONN -e 'select count(id) from final_app_safe where tencent_safe=0 and status=0 and deleted_at is null') | awk '{print $2}'
}

app_temp_file=/tmp/verification_delete_files_apps
function get_apps()
{
    local count=$1
    $MYSQL_CONN -e "select final_app_safe.id as id, concat('vol',vol_id,'/',file_path) as real_file_path from final_app_safe join final_app on final_app_safe.final_app_id=final_app.id where final_app_safe.tencent_safe = 0 and final_app_safe.status = 0 limit $count" > $app_temp_file
    tail $app_temp_file -n$(($(cat $app_temp_file | wc -l) - 1)) > $app_temp_file.1
    mv -f $app_temp_file.1 $app_temp_file
}

function del_apps()
{
    if [[ `cat $app_temp_file | wc -l` -eq 0 ]];then
        echo 'no app need to update.'
        return
    fi
    local dir=/mnt/ctappstore6/bak/$(date +%Y)/$(date +%m)/$(date +%d)/$RANDOM
    cat $app_temp_file | while read id path;do
        local count=$(ls /mnt/ctappstore*/$path | wc -l)
        local real_path=$(ls /mnt/ctappstore*/$path)
        if [[ ! $count -eq 1 ]]; then
            echo found more than one file for final_app_safe\(id=$id\), will ignore: $real_path
            continue
        fi
        echo delete file: $real_path
        sudo mkdir -p $dir
        test -f $real_path || echo file $real_path must be a file.
        test -f $real_path && sudo mv -v $real_path $dir/${real_path//\//_}
    done
}

function update_db()
{
    if [[ `cat $app_temp_file | wc -l` -eq 0 ]];then
        echo 'no app need to update.'
        return
    fi
    local ids=$(cat $app_temp_file | awk '{print $1}' | tr '\n' ',' | sed 's/^\(.*\),$/\1/g')
    echo $MYSQL_CONN -e "update final_app_safe set status=1, deleted_at=now() where id in ($ids)"
    $MYSQL_CONN -e "update final_app_safe set status=1, deleted_at=now() where id in ($ids)"
}


mail_to=gmliao@bainainfo.com,jliang@bainainfo.com,jli@bainainfo.com,jjpan@bainainfo.com

function send_mail()
{
    local count=100
    $MYSQL_CONN -e "set character_set_client=utf8;set character_set_connection=utf8;set character_set_results=utf8;select final_app.name as name, final_app.source as source, final_app.last_crawl as crawl_time, final_app.package_name as package_name, final_app.version as version, final_app.version_code as version_code, concat('http://estoredwnld7.189store.com/downloads/vol',vol_id,'/',file_path) as url, substring(info, locate('virusdesc\":', info)+13, locate('\", \"', info, locate('virusdesc\":', info)) - locate('virusdesc\":', info) - 13) as virus from final_app_safe join final_app on final_app_safe.final_app_id=final_app.id where final_app_safe.tencent_safe = 0 and date(final_app_safe.deleted_at) = date(now()) limit $count" > $app_temp_file.mail
    tail $app_temp_file.mail -n$(($(cat $app_temp_file.mail | wc -l) - 1)) > $app_temp_file.mail.1
    mv -f $app_temp_file.mail.1 $app_temp_file.mail

(echo "From: gmliao@ct-182-140-141-56
To: $mail_to
MIME-Version: 1.0
Content-Type: text/html;
Subject: Virus APK Deleted at `date -d'-1 day' +'%Y-%m-%d'`.

<html> 
<head>
<title>HTML E-mail</title>
</head>
<body>
<table border='1'>
<tr>
<td>应用名</td><td>包名</td><td>版本号</td><td>版本编号</td><td>来源</td><td>爬取时间</td><td>url</td><td>病毒信息</td>
</tr>
"

cat $app_temp_file.mail | head -n100 | while read name src ct pn v vc url virus;do
virus=$(python -c "print u\"$virus\".encode(\"utf-8\")")
ct=$(date -d"@$ct" +'%Y-%m-%d %H:%M:%S')
echo "<tr>
<td>$name</td><td>$pn</td><td>$v</td><td>$vc</td><td>$src</td><td>$ct</td><td><a href='$url'>click this</a></td><td>$virus</td>
</tr>"
done

echo "</table>
...
</body>
</html>
") | sendmail -t
}

function main()
{
    a=$(app_count)
    while [[ ! $a -eq 0 ]];do
        get_apps 50
        del_apps
        update_db
        a=$(app_count)
    done
    send_mail
}

echo will delete $(app_count) apps

main

