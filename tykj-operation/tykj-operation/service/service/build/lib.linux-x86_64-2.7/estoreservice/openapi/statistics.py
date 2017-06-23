#coding:utf8
from estorecore.db import MongodbStorage
class StatistcMongoDB(MongodbStorage):
    db_name = 'statistics'
    table_name_head = 'statis_'
    def __init__(self,others_value):
        super(StatistcMongoDB,self).__init__(others_value,self.db_name)

    def insert_to_StatisticDB(self,value_dict):
        if not isinstance(value_dict,dict):
            return False
        else:
            if "sd_csubjectid" in value_dict:
                table_name=self.table_name_head+"subjectdetail"
            else:
                table_name=self.table_name_head+"moduledetail"
            try:
                # self.upsert_item(table_name,cond={'log_date':'AaBbCcDdEe-a'},item=value_dict,upsert=True,multi=True)
                # StatistcMongoDB.upsert_item(self,table_name,cond={'log_date':'AaBbCcDdEe-a'},item=value_dict,upsert=True,multi=True)
                self.insert_item(table_name,value_dict)
            except Exception,e:
                return False
            else:
                return True