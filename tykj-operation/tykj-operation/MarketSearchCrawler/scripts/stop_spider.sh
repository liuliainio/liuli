#!/bin/bash
sudo service scrapyd stop

pids=`ps ax | grep 'scrapyd.runner' | grep '\(hiapk\|goapk\|nduoa\|mumayi\|aimi8\|eoemarket\|market.android\|soft.3g\|game.3g\)' | awk '{print $1}' | awk 'BEGIN{RS=""}{for(i=1; i<=NF; i++) {p=p" "$i} print p}'`
if [ $pids ]
then
    sudo kill -9 $pids
fi

sudo service scrapyd start