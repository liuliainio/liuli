'''
Created on Jun 20, 2011

@author: yan
'''
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from settings import SERVICE_CONFIG
from gen import Links
from gen.ttypes import LinkPredicate


def get_apk_links(source, pendings):
    apks = _thrift_call(lambda c: c.getApkLinks(LinkPredicate(source), pendings))
    return [(apk.source_link, apk.url, apk.size) for apk in apks] if apks else []


def get_update_apk_links(source, pendings):
    apks = _thrift_call(lambda c: c.getUpdateApkLinks(LinkPredicate(source), pendings))
    return [(apk.source_link, apk.url, apk.size) for apk in apks] if apks else []


def get_apk_files(source, pendings):
    apk_files = _thrift_call(lambda c: c.getApkFiles(LinkPredicate(source), pendings))
    return [(apk.source_link, apk.url, apk.source, apk.vol_id) for apk in apk_files] if apk_files else []


def get_dup_apk_files(source, pendings):
    apk_files = _thrift_call(lambda c: c.getDupApkFiles(LinkPredicate(source), pendings))
    return [(apk.source_link, apk.url, apk.source, apk.vol_id) for apk in apk_files] if apk_files else []


def get_uniq_apk_files(source, pendings):
    apk_files = _thrift_call(lambda c: c.getUniqApkFiles(LinkPredicate(source), pendings))
    return [(apk.source_link, apk.url, apk.source, apk.vol_id) for apk in apk_files] if apk_files else []


def report_apk_status(status_list):
    return _thrift_call(lambda c: c.reportApkStatus(status_list))


def report_apk_file_status(status_list):
    return _thrift_call(lambda c: c.reportApkFileStatus(status_list))


def report_dup_apk_file_status(status_list):
    return _thrift_call(lambda c: c.reportDupApkFileStatus(status_list))


def report_uniq_apk_file_status(status_list):
    return _thrift_call(lambda c: c.reportUniqApkFileStatus(status_list))


def insert_apk(status_list):
    return _thrift_call(lambda c: c.reportInsertApk(status_list))


def remove_apk(status_list):
    return _thrift_call(lambda c: c.reportRemoveApk(status_list))


def _thrift_call(func):
    try:
        transport = TSocket.TSocket(SERVICE_CONFIG['host'], SERVICE_CONFIG['port'])
        transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        client = Links.Client(protocol)
        transport.open()
        return func(client)
    except Thrift.TException as tx:
        print tx
    finally:
        transport.close()

