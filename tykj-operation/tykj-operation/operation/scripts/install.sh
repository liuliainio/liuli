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

PROJECT=operation
USER=estore

PTH_FILE='estore-operation.pth'
if [ "$2" = "lib" ] ; then
    sudo python setup.py -q install
else
    sudo python scripts/install.py
fi

echo "Collect Static to  Webfront "
pushd estoreoperation
python manage.py collectstatic
popd


echo Configuring ${PROJECT}...

echo Installing operation...
[ -z `grep "^$USER:" /etc/passwd` ] && sudo useradd -r $USER -M -N

chmod -R a+rw /var/app/data/$PROJECT
chmod -R a+rw /var/app/log/$PROJECT
chown $USER:nogroup /var/app/data/$PROJECT
chown $USER:nogroup /var/app/log/$PROJECT

ln -sf /var/app/enabled/$PROJECT/scripts/estore-operation-init.sh /etc/init.d/estore-operation
update-rc.d estore-operation defaults

ln -sf /var/app/enabled/$PROJECT/scripts/apk_scan.py /usr/local/bin/scan-apks
cp /var/app/enabled/$PROJECT/scripts/scan_apks.cron /etc/cron.d/scan-apks
