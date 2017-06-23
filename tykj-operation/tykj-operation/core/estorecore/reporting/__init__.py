from reporter import Reporter
from storage import ReportStorage


def get_reporter(report_name):
    storage = ReportStorage()
    reporter = Reporter(storage, report_name)

    return reporter
