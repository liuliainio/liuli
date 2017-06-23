#!/bin/bash

while [ 1 -eq 1 ]; do
    sudo bash -c "export PYTHONPATH=.. && python downloader.py $1 update >> /tmp/downloader_$1.log"
    sleep 60
done
