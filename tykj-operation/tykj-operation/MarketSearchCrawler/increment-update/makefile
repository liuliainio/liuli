HOST=open-api2
DEP_DIR=$(shell echo dep/`date +%Y%m%d_%H%M%S`)
PROJ_DIR=/var/app/enabled/download-interception/

test:
	echo ${DEP_DIR}
	echo ${PROJ_DIR}

dep:
	ssh ${HOST} "sudo pip install pika"
	ssh ${HOST} "mkdir -p ${DEP_DIR}"
	scp scripts/* ${HOST}:${DEP_DIR}
	ssh ${HOST} "cd ${DEP_DIR} && sudo mkdir -pv ${PROJ_DIR} && sudo cp -fv ./* ${PROJ_DIR} && sudo cp -fv ./download-interception.cron /etc/cron.d/download-interception"


SCRIPT = tail -n20 /var/app/log/download_interception/cron.log
log:
	ssh open-api3 '${SCRIPT}'
	ssh open-api4 '${SCRIPT}'
	ssh open-api5 '${SCRIPT}'
	ssh open-api1 '${SCRIPT}'
	ssh open-api2 '${SCRIPT}'

dep-all:
	make dep HOST=open-api1
	make dep HOST=open-api2
	make dep HOST=open-api3
	make dep HOST=open-api4
	make dep HOST=open-api5

