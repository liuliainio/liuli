'''
Created on Jun 20, 2011

@author: yan
'''
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from MarketSearch.settings import SERVICE_CONFIG
from MarketSearch.utils import log_error
from MarketSearch.gen import Links
from MarketSearch.gen.ttypes import LinkPredicate


def get_links(source, pendings):
    links = _thrift_call(lambda c: c.getLinks(LinkPredicate(source), pendings))
    return [link.url for link in links] if links else []


def get_update_links(source, pendings):
    links = _thrift_call(lambda c: c.getUpdateLinks(LinkPredicate(source), pendings))
    return [link.url for link in links] if links else []


def report_status(status_list):
    return _thrift_call(lambda c: c.reportStatus(status_list))


def report_update_status(status_list):
    return _thrift_call(lambda c: c.reportUpdateStatus(status_list))


def _thrift_call(func):
    try:
        transport = TSocket.TSocket(SERVICE_CONFIG['host'], SERVICE_CONFIG['port'])
        transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        client = Links.Client(protocol)
        transport.open()
        return func(client)
    except Thrift.TException as tx:
        log_error(tx)
    finally:
        transport.close()

