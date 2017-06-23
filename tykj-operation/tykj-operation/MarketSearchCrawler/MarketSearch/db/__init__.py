from MarketSearch.settings import DB_CONFIG, QUEUE_CONFIG
from MarketSearch.db import market

market.config(DB_CONFIG['host'], DB_CONFIG['user'], DB_CONFIG['password'], DB_CONFIG['db'])

market.init_queue(QUEUE_CONFIG['host'], QUEUE_CONFIG['port'], QUEUE_CONFIG['password'])
