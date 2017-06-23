#!/bin/sh

service estore-operation start
MANAGE_DIR=/var/app/enabled/operation/estoreoperation/
APK_PATCH_PID=/var/run/estore-apkpatch.pid

if [ -f "$APK_PATCH_PID" ]; then
    echo "apk patch is already running."
else
    pushd ${MANAGE_DIR} >/dev/null
    python manage.py apkpatch start >> /tmp/estore-apkpatch.log 2>&1
    popd >/dev/null
fi 