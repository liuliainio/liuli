PROJ_NAME = MarketSearchService
INSTALL_DST = /var/app/enabled/${PROJ_NAME}
LOG_DST = /var/app/log/${PROJ_NAME}
SERVICE_FILE = service.conf
SERVICE_FILE1 = apkpatch-service.conf

install:
	-test -d '${INSTALL_DST}.bak' && sudo rm -rf '${INSTALL_DST}.bak'
	-test -d '${INSTALL_DST}' && sudo cp -rf '${INSTALL_DST}' '${INSTALL_DST}.bak'
	sudo rm -rf ${INSTALL_DST}
	sudo mkdir -p '${INSTALL_DST}'
	sudo chmod a+rw '${INSTALL_DST}'
	cp -r ../* '${INSTALL_DST}'
	sudo mkdir -p '${LOG_DST}'
	sudo chmod a+rw '${LOG_DST}'
	sudo cp -fv ${SERVICE_FILE} /etc/init/${PROJ_NAME}-${SERVICE_FILE}
	sudo restart ${PROJ_NAME}-service || sudo start ${PROJ_NAME}-service
	sudo cp -fv ${SERVICE_FILE1} /etc/init/${PROJ_NAME}-${SERVICE_FILE1}
	sudo restart ${PROJ_NAME}-apkpatch-service || sudo start ${PROJ_NAME}-apkpatch-service


update: 


