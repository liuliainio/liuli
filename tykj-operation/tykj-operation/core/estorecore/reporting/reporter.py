#!/usr/bin/env python
import socket
import getpass
import datetime

from django.template import loader
from django.core.mail import mail_admins

_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def _get_server_ip():
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.connect(('google.com', 80))
    ip = sock.getsockname()[0]
    sock.close()
    return ip


class Reporter(object):

    def __init__(self, storage, report_name="Default Report"):
        self.storage = storage
        self.name = report_name

    def collect_report(self, infos, **kwargs):
        self.storage.save(infos, **kwargs)

    def send_report(self):
        report_time = datetime.datetime.now().strftime(_DATETIME_FORMAT)
        subject = "%s at %s" % (self.name, report_time)
        user_name = getpass.getuser()
        host_infos = socket.gethostbyname_ex(socket.gethostname())
        report = loader.render_to_string("report_table.html", {
                    "report_name": self.name,
                    "server_ip": _get_server_ip(),
                    "host_name": "%s@%s" % (user_name, host_infos[0]),
                    "report_time": report_time,
                    "report_list": self.storage.report_list
                })
        mail_admins(subject, report, html_message=report)
