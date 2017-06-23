
dep:
	./release/deploy.sh dep ct-crawler ' '

dep-crawler1:
	./release/deploy.sh dep ct-crawler1 ' '

dep-crawler2:
	./release/deploy.sh dep ct-crawler2 ' '

dep-crawler3:
	./release/deploy.sh dep ct-crawler3 ' '

dep-crawler4:
	./release/deploy.sh dep ct-crawler4 ' '

dep-open-in-crawler:
	./release/deploy.sh dep open-in-crawler ' '


HOSTS = ct-crawler ct-crawler1 ct-crawler2 ct-crawler3 ct-crawler4
CMD = echo ok

ssh-cmd:
	for h in ${HOSTS};do \
		ssh $$h "${CMD}"; \
		echo '##############################################'; \
	done

dep-all:
	./release/deploy.sh dep ct-crawler1 ' '
	./release/deploy.sh dep ct-crawler2 ' '
	./release/deploy.sh dep ct-crawler3 ' '


stop-downloader:
	make ssh-cmd CMD="ps aux | grep download.sh | grep -v grep && ps aux | grep download.sh | grep -v grep | awk '{print \\\$$\$$2}' | xargs sudo kill -9" 'HOSTS=ct-crawler ct-crawler2 ct-crawler3'

status-downloader:
	make ssh-cmd CMD="ps aux | grep download.sh | grep -v grep" 'HOSTS=${HOSTS}'




