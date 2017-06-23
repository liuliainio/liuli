# -*- coding: utf-8 -*-
from estorecore.db import MongodbStorage


CITY_INDEX_DICT = {
    u'安徽': 1,
    u'北京': 2,
    u'重庆': 3,
    u'福建': 4,
    u'甘肃': 5,
    u'广东': 6,
    u'广西': 7,
    u'贵州': 8,
    u'海南': 9,
    u'河北': 10,
    u'河南': 11,
    u'黑龙江': 12,
    u'湖北': 13,
    u'湖南': 14,
    u'吉林': 15,
    u'江苏': 16,
    u'江西': 17,
    u'辽宁': 18,
    u'内蒙古': 19,
    u'宁夏': 20,
    u'青海': 21,
    u'山东': 22,
    u'山西': 23,
    u'陕西': 24,
    u'上海': 25,
    u'四川': 26,
    u'天津': 27,
    u'西藏': 28,
    u'新疆': 29,
    u'云南': 30,
    u'浙江': 31,
}
CITY_INDEX_OTHER = 100


class LocationMongodbStorage(MongodbStorage):
    db_name = "location"


    def __init__(self, conn_str):
        super(LocationMongodbStorage, self).__init__(conn_str, self.db_name)

    def ip_to_city(self, ip):
        if not ip:
            return (None, None)

        location = self._query_ip(ip)
        if not location:
            return (CITY_INDEX_OTHER, None)

        location = location.get("location")
        if location is None or 'raw' not in location:
            return (CITY_INDEX_OTHER, None)

        for i in range(2, 3):
            city_index = CITY_INDEX_DICT.get(location['raw'][0:i], -1)
            if city_index != -1:
                return (city_index, location['raw'])
        return (CITY_INDEX_OTHER, location['raw'])


    def _query_ip(self, ip):
        return self._ip_lte(self._ip2int(ip))


    def _ip_lte(self, ip):
        cond = {"ip" : {"$lte" : ip}}
        results = self._db.ip.find(cond).sort("ip", -1).limit(1)
        results = [r for r in results]
        if not results:
            return None
        return results[0]


    def _ip2int(self, ip):
        if not isinstance(ip, basestring):
            return ip

        words = ip.split('.')
        return (int(words[0])<<24) + (int(words[1])<<16) + (int(words[2])<<8) + (int(words[3]))
