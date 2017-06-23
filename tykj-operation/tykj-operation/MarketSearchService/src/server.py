'''
Created on Jun 27, 2011

@author: yan
'''
from multiprocessing.synchronize import Lock
import db
from MarketSearch.gen import Links
from MarketSearch.gen.ttypes import Link, Apk, ApkFile
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
import datetime

_lock = Lock()


class LinksHandler(Links.Iface):

    DEFAULT_PORT = 8555

    def getLinks(self, predicate, pendings):
        try:
            _lock.acquire()
            begin = datetime.datetime.now()
            print "[%s]get links ..." % predicate.source
            result = db.get_links(predicate.source, pendings)
            end  = datetime.datetime.now()
            delta =end - begin
            print "getLinks %s; begin=%s; end=%s; cost=%s" %(predicate.source, begin, end, delta.seconds)
            return [Link(link[0]) for link in result] if result else []
        finally:
            _lock.release()

    def getUpdateLinks(self, predicate, pendings):
        try:
            _lock.acquire()
            begin = datetime.datetime.now()
            print "[%s]get update links ..." % predicate.source
            result = db.get_update_links(predicate.source, pendings)
            end  = datetime.datetime.now()
            delta =end - begin
            print "getUpadteLinks %s; begin=%s; end=%s; cost=%s" %(predicate.source, begin, end, delta.seconds)
            return [Link(link[0]) for link in result] if result else []
        finally:
            _lock.release()

    def getApkLinks(self, predicate, pendings):
        try:
            _lock.acquire()
            begin = datetime.datetime.now()
            print "[%s]get apk links ..." % predicate.source
            result = db.get_apk_links(predicate.source, pendings)
            end  = datetime.datetime.now()
            delta =end - begin
            print "getApkLinks %s; begin=%s; end=%s; cost=%s" %(predicate.source, begin, end, delta.seconds)
            return [Apk(apk[0], apk[1], apk[2]) for apk in result] if result else []
        finally:
            _lock.release()

    def getUpdateApkLinks(self, predicate, pendings):
        print datetime.datetime.now(), "[%s]wait to get update apk links ..." % predicate.source
        try:
            _lock.acquire()
            begin = datetime.datetime.now()
            print datetime.datetime.now(), "[%s]get update apk links ..." % predicate.source
            result = db.get_update_apk_links(predicate.source, pendings)
            end  = datetime.datetime.now()
            delta =end - begin
            print "getUpdateApkLinks %s; begin=%s; end=%s; cost=%s" %(predicate.source, begin, end, delta.seconds)
            return [Apk(apk[0], apk[1], apk[2]) for apk in result] if result else []
        finally:
            _lock.release()

    def getApkFiles(self, predicate, pendings):
        try:
            _lock.acquire()
            begin = datetime.datetime.now()
            print "[%s]get apk files ..." % predicate.source
            result = db.get_apk_files(predicate.source, pendings)
            end  = datetime.datetime.now()
            delta =end - begin
            print "getApkFiles %s; begin=%s; end=%s; cost=%s" %(predicate.source, begin, end, delta.seconds)
            return [ApkFile(apk[0], apk[1], apk[2], apk[3]) for apk in result] if result else []
        finally:
            _lock.release()

    def getDupApkFiles(self, predicate, pendings):
        try:
            _lock.acquire()
            begin = datetime.datetime.now()
            print "[%s]get dup apk files ..." % predicate.source
            result = db.get_dup_apk_files(predicate.source, pendings)
            end  = datetime.datetime.now()
            delta =end - begin
            print "getDupApkFiles %s; begin=%s; end=%s; cost=%s" %(predicate.source, begin, end, delta.seconds)
            return [ApkFile(apk[0], apk[1], apk[2], apk[3]) for apk in result] if result else []
        finally:
            _lock.release()

    def getUniqApkFiles(self, predicate, pendings):
        try:
            _lock.acquire()
            begin = datetime.datetime.now()
            print "[%s]get uniq apk files ..." % predicate.source
            result = db.get_uniq_apk_files(predicate.source, pendings)
            end  = datetime.datetime.now()
            delta =end - begin
            print "getUniqApkFiles %s; begin=%s; end=%s; cost=%s" %(predicate.source, begin, end, delta.seconds)
            return [ApkFile(apk[0], apk[1], apk[2], apk[3]) for apk in result] if result else []
        finally:
            _lock.release()

    def reportStatus(self, statusList):
        try:
            _lock.acquire()
            begin = datetime.datetime.now()
            print "report status ..."
            if statusList[0].pages:
                print "status:%s, type:%s, pages:%s" % (statusList[0].status, statusList[0].type, statusList[0].pages)
            db.update_links(statusList)
            end  = datetime.datetime.now()
            delta =end - begin
            print "reportStatus %s; begin=%s; end=%s; cost=%s" %("", begin, end, delta.seconds)
        finally:
            _lock.release()

    def reportUpdateStatus(self, statusList):
        try:
            _lock.acquire()
            begin = datetime.datetime.now()
            print "report update status ..."
            if statusList[0].pages:
                print "status:%s, type:%s, pages:%s" % (statusList[0].status, statusList[0].type, statusList[0].pages)
            db.update_update_links(statusList)
            end  = datetime.datetime.now()
            delta =end - begin
            print "reportUpdateStatus %s; begin=%s; end=%s; cost=%s" %("", begin, end, delta.seconds)
        finally:
            _lock.release()
    
    def reportApkStatus(self, statusList):
        try:
            _lock.acquire()
            begin = datetime.datetime.now()
            print "report apk status ..."
            print "status:%s, vol_id:%s, url:%s" % (statusList[0].status, statusList[0].vol_id, statusList[0].url)
            db.update_apk_links(statusList)
            end  = datetime.datetime.now()
            delta =end - begin
            print "reportApkStatus %s; begin=%s; end=%s; cost=%s" %("", begin, end, delta.seconds)
        finally:
            _lock.release()

    def reportApkFileStatus(self, statusList):
        try:
            _lock.acquire()
            begin = datetime.datetime.now()
            print "report apk file status ..."
            db.update_apk_files(statusList)
            end  = datetime.datetime.now()
            delta =end - begin
            print "reportApkFileStatus %s; begin=%s; end=%s; cost=%s" %("", begin, end, delta.seconds)
        finally:
            _lock.release()

    def reportDupApkFileStatus(self, statusList):
        try:
            _lock.acquire()
            begin = datetime.datetime.now()
            print "report dup apk file status ..."
            db.update_dup_apk_files(statusList)
            end  = datetime.datetime.now()
            delta =end - begin
            print "reportDupApkFileStatus %s; begin=%s; end=%s; cost=%s" %("", begin, end, delta.seconds)
        finally:
            _lock.release()

    def reportUniqApkFileStatus(self, statusList):
        try:
            _lock.acquire()
            begin = datetime.datetime.now()
            print "report uniq apk file status ..."
            db.update_uniq_apk_files(statusList)
            end  = datetime.datetime.now()
            delta =end - begin
            print "reportUniqApkFileStatus %s; begin=%s; end=%s; cost=%s" %("", begin, end, delta.seconds)
        finally:
            _lock.release()

    def reportInsertApk(self, statusList):
        try:
            _lock.acquire()
            begin = datetime.datetime.now()
            print "report insert apk file status ..."
            db.insert_apk_files(statusList)
            end  = datetime.datetime.now()
            delta =end - begin
            print "reportInsertApk %s; begin=%s; end=%s; cost=%s" %("", begin, end, delta.seconds)
        finally:
            _lock.release()


    def reportRemoveApk(self, statusList):
        try:
            _lock.acquire()
            begin = datetime.datetime.now()
            print "report remove apk file status ..."
            db.remove_apk_files(statusList)
            end  = datetime.datetime.now()
            delta =end - begin
            print "reportRemoveApk %s; begin=%s; end=%s; cost=%s" %("", begin, end, delta.seconds)
        finally:
            _lock.release()


handler = LinksHandler()
processor = Links.Processor(handler)
transport = TSocket.TServerSocket(port=LinksHandler.DEFAULT_PORT)
tfactory = TTransport.TBufferedTransportFactory()
pfactory = TBinaryProtocol.TBinaryProtocolFactory()

server = TServer.TThreadedServer(processor, transport, tfactory, pfactory)

print "Starting server..."
server.serve()
