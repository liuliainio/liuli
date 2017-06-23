
dep-test:
	./release/deploy.sh -t dep -h ct-crawler-test

dep:
	./release/deploy.sh  -t dep -h ct-crawler 

dep-crawler1:
	./release/deploy.sh -t dep -h ct-crawler1

dep-crawler2:
	./release/deploy.sh -t dep -h ct-crawler2

dep-crawler3:
	./release/deploy.sh -t dep -h ct-crawler3

dep-crawler4:
	./release/deploy.sh -t dep -h ct-crawler4

dep-open-in-crawler:
	./release/deploy.sh -t dep -h open-in-crawler

dep-all:dep dep-crawler1 dep-crawler2 dep-crawler3 dep-crawler4

dep-interception:dep-crawler1 dep-crawler2 dep-crawler3 dep-crawler4

dep-incrementupdate-master:
	./release/deploy.sh -t dep -h ct-crawler -s urlmaster

dep-incrementupdate-downloadlinkcrawler:
	./release/deploy.sh -t dep -h ct-crawler2 -s downloadlinkcrawler

dep-incrementupdate-urlconsumer:
	./release/deploy.sh -t dep -h ct-crawler1 -s urlconsumer
	./release/deploy.sh -t dep -h ct-crawler2 -s urlconsumer
	./release/deploy.sh -t dep -h ct-crawler3 -s urlconsumer
	./release/deploy.sh -t dep -h ct-crawler4 -s urlconsumer


LOG_CHECK_SCRIPT = 'tail -n50 /var/app/log/MarketSearchCrawler/interception_service.log'
interception-log:
	ssh ct-crawler '${LOG_CHECK_SCRIPT}'
	echo '##############################################'
	ssh ct-crawler1 '${LOG_CHECK_SCRIPT}'
	echo '##############################################'
	ssh ct-crawler2 '${LOG_CHECK_SCRIPT}'
	echo '##############################################'
	ssh ct-crawler3 '${LOG_CHECK_SCRIPT}'
	echo '##############################################'
	ssh ct-crawler4 '${LOG_CHECK_SCRIPT}'

VERIFICATION_LOG_CHECK_SCRIPT = 'tail -n20 /var/app/log/MarketSearchCrawler/verification_service.log'
verification-log:
	ssh ct-crawler1 '${VERIFICATION_LOG_CHECK_SCRIPT}'
	echo '##############################################'
	ssh ct-crawler2 '${VERIFICATION_LOG_CHECK_SCRIPT}'
	echo '##############################################'
	ssh ct-crawler3 '${VERIFICATION_LOG_CHECK_SCRIPT}'
	echo '##############################################'
	ssh ct-crawler4 '${VERIFICATION_LOG_CHECK_SCRIPT}'

incrementupdate-log:
	make ssh-cmd HOSTS='ct-crawler1 ct-crawler2 ct-crawler3 ct-crawler4' CMD="tail -n20 /var/app/log/MarketSearchCrawler/incrementupdate-urls.log"

clean-urlconsumer:
	make ssh-cmd HOSTS='ct-crawler1 ct-crawler2 ct-crawler3 ct-crawler4' CMD="cd /var/app/enabled/MarketSearchCrawler && make consumer-clean-urlconsumer"

consumer-clean-urlconsumer:
	pid=`ps aux | grep incrementupdate/rabbit | grep python | tail -n+2 | awk '{print $$2}'`; find /tmp/incrementupdate/ | grep -v $$pid | grep /tmp/incrementupdate/incrementupdate | xargs sudo rm -v


restart-urlconsumer:
	make ssh-cmd HOSTS='ct-crawler1 ct-crawler2 ct-crawler3 ct-crawler4' CMD="ps aux | grep incrementupdate/rabbit | grep -v grep | awk '{print \\\$$\$$2}' | xargs sudo kill -9"

restart-verification:
	make ssh-cmd HOSTS='ct-crawler1 ct-crawler2 ct-crawler3 ct-crawler4' CMD="ps aux | grep verification/rabbit | grep -v grep | awk '{print \\\$$\$$2}' | xargs sudo kill -9"

restart-interception:
	make ssh-cmd HOSTS='ct-crawler1 ct-crawler2 ct-crawler3 ct-crawler4' CMD="ps aux | grep interception/rabbit | grep -v grep | awk '{print \\\$$\$$2}' | xargs sudo kill -9"


HOSTS = ct-crawler ct-crawler1 ct-crawler2 ct-crawler3 ct-crawler4
CMD = echo ok

ssh-cmd:
	for h in ${HOSTS};do \
		ssh $$h "${CMD}"; \
		echo '##############################################'; \
	done


stop-downloader:
	make ssh-cmd CMD="ps aux | grep download.sh | grep -v grep && ps aux | grep download.sh | grep -v grep | awk '{print \\\$$\$$2}' | xargs sudo kill -9" 'HOSTS=ct-crawler ct-crawler2 ct-crawler3'

status-downloader:
	make ssh-cmd CMD="ps aux | grep download.sh | grep -v grep" 'HOSTS=ct-crawler ct-crawler2 ct-crawler3'




restore-crawler-data:
	mysql -uroot -p1111 market < scripts/update_link.sql

install-deps:
	sudo apt-get install python-lxml python-openssl python-twisted python-mysqldb redis
	sudo pip install scrapy==0.14.4 redis_queue

install-rabbit-mq:
	grep 'deb http://www.rabbitmq.com/debian/ testing main' /etc/apt/sources.list || \
		(sudo bash -c "echo 'deb http://www.rabbitmq.com/debian/ testing main' >> /etc/apt/sources.list")
	wget http://www.rabbitmq.com/rabbitmq-signing-key-public.asc -O /tmp/rabbitmq-signing-key-public.asc
	sudo apt-key add /tmp/rabbitmq-signing-key-public.asc
	rm /tmp/rabbitmq-signing-key-public.asc
	-sudo apt-get update
	sudo apt-get -y install rabbitmq-server
	sudo rabbitmq-plugins enable rabbitmq_management
	sudo service rabbitmq-server restart
	-test -f /usr/local/bin/rabbitmqadmin || sudo bash -c 'curl http://localhost:15672/cli/rabbitmqadmin > /usr/local/bin/rabbitmqadmin && chmod a+x /usr/local/bin/rabbitmqadmin && rabbitmqadmin --bash-completion > /etc/bash_completion.d/rabbitmqadmin'
	sudo pip install pika





