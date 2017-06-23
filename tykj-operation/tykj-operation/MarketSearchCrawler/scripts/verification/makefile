SHELL := /bin/bash

db-crawler:
	mysql -udev_market -pmarket_dev_pwd -h192.168.130.77 market


redis:
	redis-cli -h 192.168.130.76



LAST_ID_FILE=/var/app/data/MarketSearchCrawler/sync_tencent_safe.lastid
sync_tencent_safe:
	for s in 0 1 2 3;do \
		sql1="update final_app t inner join (select final_app_id from final_app_safe where tencent_safe = $$s and sync_status=0 and last_verify_time > date_sub(curdate(), interval 3 day)) a on a.final_app_id=t.id set t.tencent_safe=$$s, t.status=t.status&0xfffffffffffffff6, t.updated_at=now()"; \
		sql2="update final_app_safe set sync_status=1 where tencent_safe = $$s and last_verify_time > date_sub(curdate(), interval 3 day) and sync_status = 0"; \
		mysql -udev_market -pmarket_dev_pwd -h192.168.130.77 market -e "set autocommit=false;$$sql1;$$sql2;commit;"; \
	done
	count=$$(mysql -udev_market -pmarket_dev_pwd -h192.168.130.77 market -e "select count(*) from final_app_safe where sync_status=1" | tail -n1); \
		count1=$$(mysql -udev_market -pmarket_dev_pwd -h192.168.130.77 market -e "select count(*) from final_app where tencent_safe is not null" | tail -n1); \
		echo synced apps in final_app_safe: $$count, in final_app: $$count1
	mkdir -p `dirname ${LAST_ID_FILE}`
	[ -f ${LAST_ID_FILE} ] || echo 0 > ${LAST_ID_FILE}; \
		lastid=$$(<${LAST_ID_FILE}); \
		lastid1=$$(mysql -udev_market -pmarket_dev_pwd -h192.168.130.77 market -e "select id from final_app_safe where id >= $$lastid limit 1000,1" | tail -n 1); \
		test "x$$lastid1" == "x" && lastid1=$$(mysql -udev_market -pmarket_dev_pwd -h192.168.130.77 market -e "select max(id) from final_app_safe" | tail -n 1); \
		echo will sync id from $$lastid to $$lastid1; \
		for s in 0 1 2 3;do \
			sql1="update final_app t inner join (select final_app_id from final_app_safe where tencent_safe = $$s and sync_status=0 and id >= $$lastid and id < $$lastid1) a on a.final_app_id=t.id set t.tencent_safe=$$s, t.status=t.status&0xfffffffffffffff6, t.updated_at=now()"; \
			sql2="update final_app_safe set sync_status = 1 where id >= $$lastid and id < $$lastid1 and tencent_safe=$$s"; \
			mysql -udev_market -pmarket_dev_pwd -h192.168.130.77 market -e "set autocommit=false;$$sql1;$$sql2;commit;"; \
		done; \
		echo $$lastid1 > ${LAST_ID_FILE}
	count=$$(mysql -udev_market -pmarket_dev_pwd -h192.168.130.77 market -e "select count(*) from final_app_safe where sync_status=1" | tail -n1); \
		count1=$$(mysql -udev_market -pmarket_dev_pwd -h192.168.130.77 market -e "select count(*) from final_app where tencent_safe is not null" | tail -n1); \
		echo synced apps in final_app_safe: $$count, in final_app: $$count1
