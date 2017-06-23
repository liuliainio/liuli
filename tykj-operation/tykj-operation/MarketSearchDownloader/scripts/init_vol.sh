init_vol()
{
all=$(df |grep $1$2|tr -s " " |cut -d " " -f2)
used=$(df | grep $1$2|tr -s " " |cut -d " " -f3)
echo $all
echo $used
mysql -umarket -pP@55word market -h $3 -e "insert into vol (id,total_kbytes,used_kbytes) values ("$2","$all","$used")\
 on duplicate key update total_kbytes="$all" , used_kbytes="$used";"
}

fs_root=$1
db_host=$2
for file in $(ls $fs_root);
do
init_vol $fs_root $file $db_host
done



