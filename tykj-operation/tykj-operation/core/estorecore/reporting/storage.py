

class ReportStorage(object):

    def __init__(self, report_list=[]):
        self.report_list = report_list

    def save(self, infos, **kwargs):
        self.report_list.append(infos)
