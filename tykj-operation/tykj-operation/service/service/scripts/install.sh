#!/bin/bash
#
# This scripts is used to install the application.
# This scripts is required for all projects.
#
#
#
SCRIPT_DIR=`dirname $0`

if [ "$1" = "checkdeps" ] ; then
	echo "Checking and installing dependecies..."
    if [ -f "${SCRIPT_DIR}/install_deps.sh" ]; then
        ${SCRIPT_DIR}/install_deps.sh
	else
		echo "Depedency install script not found."		
    fi
fi

PROJECT=service
USER=estore

PTH_FILE='estore-service.pth'
if [ "$2" = "lib" ] ; then
    sudo python setup.py -q install
else
    pwd > ${PTH_FILE}
    sudo python scripts/install.py
fi

echo Configuring ${PROJECT}...

echo Installing service...
[ -z `grep "^$USER:" /etc/passwd` ] && sudo useradd -r $USER -M -N

chmod -R a+rw /var/app/data/$PROJECT
chmod -R a+rw /var/app/log/$PROJECT
chown $USER:nogroup /var/app/data/$PROJECT
chown $USER:nogroup /var/app/log/$PROJECT

ln -sf /var/app/enabled/$PROJECT/scripts/estore-service-init.sh /etc/init.d/estore-service
update-rc.d estore-service defaults
cp -f /var/app/enabled/$PROJECT/scripts/estore-service.cron /etc/cron.d/estore-service
