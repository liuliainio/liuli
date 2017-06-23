#!/bin/bash
#
# Estore operation init script
# 
### BEGIN INIT INFO
# Provides:          estore-operation
# Required-Start:    $remote_fs $remote_fs $network $syslog
# Required-Stop:     $remote_fs $remote_fs $network $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start estore Web Site Data at boot time
# Description:       estore Web Site Data provides web server backend.
### END INIT INFO

PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin:/var/app/enabled/operation
NAME=estore-operation
DESC="estore operation Server"
PROJECT=operation
APP_DIR=/var/app/enabled/$PROJECT
LOG_DIR=/var/app/log/$PROJECT
PID_FILE=/var/run/$NAME.pid


if [ -f /etc/default/$NAME ]; then
	. /etc/default/$NAME
fi

set -e

. /lib/lsb/init-functions

function stop_operation()
{
	if [ -f "${PID_FILE}" ]; then
	    export PID=`cat ${PID_FILE}`
	    rm "${PID_FILE}"
	    kill -INT ${PID}
	else
	    echo "${NAME} stop/waiting."
	fi
}

function start_operation()
{
	if [ -f "$PID_FILE" ]; then
		echo "$NAME is already running."
	else
	    pushd ${APP_DIR} >/dev/null
	    uwsgi --pidfile=${PID_FILE} -x uwsgi.xml --uid estore --gid nogroup
	    popd >/dev/null	

	fi
}

case "$1" in
	start)
		echo -n "Starting $DESC..."
		start_operation
		echo "Done."				
		;;
	stop)
		echo -n "Stopping $DESC..."
		stop_operation
		echo "Done."
		;;

	restart)
		echo -n "Restarting $DESC..."
		stop_operation
		sleep 3
		start_operation
		echo "Done."
		;;

	status)
		status_of_proc -p $PID_FILE "$DAEMON" uwsgi && exit 0 || exit $?
		;;
	*)
		echo "Usage: $NAME {start|stop|restart|status}" >&2
		exit 1
		;;
esac

exit 0
