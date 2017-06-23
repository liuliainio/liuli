PROJ_NAME = MarketSearchDownloader
INSTALL_DST = /var/app/enabled/${PROJ_NAME}
LOG_DST = /var/app/log/${PROJ_NAME}
SERVICE_FILES = downloader-service

install:
	-test -d '${INSTALL_DST}.bak' && sudo rm -rf '${INSTALL_DST}.bak'
	-test -d '${INSTALL_DST}' && sudo cp -rf '${INSTALL_DST}' '${INSTALL_DST}.bak'
	sudo rm -rf ${INSTALL_DST}
	sudo mkdir -p '${INSTALL_DST}'
	sudo chmod a+rw '${INSTALL_DST}'
	cp -r ../* '${INSTALL_DST}'
	sudo mkdir -p '${LOG_DST}'
	sudo chmod a+rw '${LOG_DST}'
	for sf in ${SERVICE_FILES};do \
    	sudo cp -fv $$sf.conf /etc/init/${PROJ_NAME}-$$sf.conf; \
		sudo stop ${PROJ_NAME}-$$sf; \
		sudo start ${PROJ_NAME}-$$sf; \
	done

