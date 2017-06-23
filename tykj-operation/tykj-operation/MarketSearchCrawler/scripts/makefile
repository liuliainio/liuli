PROJ_NAME = MarketSearchCrawler
INSTALL_DST = /var/app/enabled/${PROJ_NAME}
LOG_DST = /var/app/log/${PROJ_NAME}
CRON_FILE = ../crawler.cron
CRON_FILE_SERVICE = ../crawler-service.cron
CRON_FILE_SERVICE_INCREMENTUPDATE_MASTER = ../crawler-service-incrementupdate.cron
SERVICE_FILE_INCREMENTUPDATE_URLCONSUMER = incrementupdate-urlconsumer
SERVICE_FILE_INCREMENTUPDATE_DOWNLOADLINK = incrementupdate-downloadlinkcrawler
SERVICE_FILES = interception-service verification-service
LOG_ROTATE_FILE = logrotate
MAKE_ARGS = 

install: update
	-test -d '${INSTALL_DST}.bak' && sudo rm -rf '${INSTALL_DST}.bak'
	-test -d '${INSTALL_DST}' && sudo cp -rf '${INSTALL_DST}' '${INSTALL_DST}.bak'
	sudo rm -rf ${INSTALL_DST}
	sudo mkdir -p '${INSTALL_DST}'
	sudo chmod a+rw '${INSTALL_DST}'
	cp -r ../* '${INSTALL_DST}'
	sudo mkdir -p '${LOG_DST}'
	sudo chmod a+rw '${LOG_DST}'
	sudo cp -fv ${LOG_ROTATE_FILE} /etc/logrotate.d/${PROJ_NAME}
	make install-${MAKE_ARGS}
	#sudo cp -fv ${CRON_FILE} /etc/cron.d/crawler
	#sudo cp -fv ${CRON_FILE_SERVICE} /etc/cron.d/crawler-service
	#sudo service redis-server status | grep running || sudo service redis-server start
	#sudo service rabbitmq-server status || sudo service rabbitmq-server start
	#for sf in ${SERVICE_FILES};do \
    #	sudo cp -fv $$sf.conf /etc/init/${PROJ_NAME}-$$sf.conf; \
	#	sudo stop ${PROJ_NAME}-$$sf; \
	#	sudo start ${PROJ_NAME}-$$sf; \
	#done

install-downloadlinkcrawler:
	sudo cp -fv ${SERVICE_FILE_INCREMENTUPDATE_DOWNLOADLINK}.conf /etc/init/${PROJ_NAME}-${SERVICE_FILE_INCREMENTUPDATE_DOWNLOADLINK}.conf
	-sudo stop ${PROJ_NAME}-${SERVICE_FILE_INCREMENTUPDATE_DOWNLOADLINK}
	sudo start ${PROJ_NAME}-${SERVICE_FILE_INCREMENTUPDATE_DOWNLOADLINK}



install-urlmaster:
	sudo cp -fv ${CRON_FILE_SERVICE_INCREMENTUPDATE_MASTER} /etc/cron.d/crawler-service-incrementupdate.cron

install-urlconsumer:
	sudo cp -fv ${SERVICE_FILE_INCREMENTUPDATE_URLCONSUMER}.conf /etc/init/${PROJ_NAME}-${SERVICE_FILE_INCREMENTUPDATE_URLCONSUMER}.conf
	-sudo stop ${PROJ_NAME}-${SERVICE_FILE_INCREMENTUPDATE_URLCONSUMER}
	sudo start ${PROJ_NAME}-${SERVICE_FILE_INCREMENTUPDATE_URLCONSUMER}

update:
	

update.v0:
	mysql -udev_market -pmarket_dev_pwd -h192.168.130.77 market < db/init.sql 

update.v1:
	cd .. && make install-rabbit-mq

update.v2:
	sudo pip install pika
	sudo pip install requests

start:
	cd ${INSTALL_DST}/CommentCrawler && python main.py

