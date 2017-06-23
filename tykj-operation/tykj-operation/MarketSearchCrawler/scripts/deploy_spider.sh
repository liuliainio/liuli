#!/bin/bash

echo "stop the spider"
sh stop_spider.sh

cd ../

echo "deploy scrapy project to scrapyd"
scrapy deploy MarketSearch -p MarketSearch

echo "start spider"
server=localhost
curl http://$server:6800/schedule.json -d project=MarketSearch -d spider=hiapk.com
curl http://$server:6800/schedule.json -d project=MarketSearch -d spider=goapk.com
curl http://$server:6800/schedule.json -d project=MarketSearch -d spider=nduoa.com
curl http://$server:6800/schedule.json -d project=MarketSearch -d spider=mumayi.com
curl http://$server:6800/schedule.json -d project=MarketSearch -d spider=aimi8.com
curl http://$server:6800/schedule.json -d project=MarketSearch -d spider=eoemarket.com
curl http://$server:6800/schedule.json -d project=MarketSearch -d spider=market.android.com
curl http://$server:6800/schedule.json -d project=MarketSearch -d spider=soft.3g.cn
curl http://$server:6800/schedule.json -d project=MarketSearch -d spider=game.3g.cn