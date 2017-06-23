#! -*- coding: utf-8 -*-
import os
import logging
import csv
from pyExcelerator import Workbook

logger = logging.getLogger("estoreoperation")

export_file_format = "xls"
export_filepath = "/var/app/data/operation/"


def export_file(data):
    global export_filename
    if export_file_format == "csv":
        export_filename = "data.csv"
        export_file_csv(data)
    elif export_file_format == "xls":
        export_filename = "data.xls"
        logger.info(export_filename)
        export_file_excel(data)


def export_file_csv(data):
    try:
        # filepath = os.path.join(export_filepath, data['downloadid'])
        filename = os.path.join(export_filepath, export_filename + '.' + data[0]['downloadid'])
        writer = csv.writer(file(filename, "wb"))
        names = []
        values = []
        for d in data:
            if "name" in d.keys():
                names.append(d['name'])
                values.append(d['data'])
        writer.writerow(names)
        for row in zip(*values):
            writer.writerow(row)
    except Exception, e:
        logger.warn(e, exc_info=True)


def export_file_excel(data):
    try:
        # filepath = os.path.join(export_filepath, data['downloadid'])
        filename = os.path.join(export_filepath, export_filename + '.' + data[0]['downloadid'])
        w = Workbook()
        ws = w.add_sheet('sheet')

        names = []
        values = []
        for d in data:
            if "name" in d.keys():
                names.append(d['name'])
                values.append(d['data'])
            # logger.info(values)
        for i in range(len(names)):
            ws.write(0, i, names[i])
        for i in range(len(values)):
            for j in range(len(values[i])):
                value = values[i][j]
                if  not value:
                    value = u''
                ws.write(j + 1, i, value)
            # i += 1
        w.save(filename)
    except Exception, e:
        logger.warn(e, exc_info=True)


def export_special_excel(filename, data, names=[]):
    full_filepath = ''
    try:
        full_filepath = os.path.join(export_filepath, filename)
        w = Workbook()
        ws = w.add_sheet('sheet')
        if not names:
            names = [u'id',u'name',u'detail_times',u'outer_times',u'total_times',u'order']
        column_length = len(names)
        for i in range(column_length):
            ws.write(0, i, names[i])
        for i,value in enumerate(data):
            for j in range(column_length):
                index_name = names[j]
                ws.write(i + 1, j, value[index_name])
        w.save(full_filepath)
    except Exception, e:
        logger.warn(e, exc_info=True)
    finally:
        return full_filepath


def export_simple_excel(filename, data):
    full_filepath = ''
    try:
        full_filepath = os.path.join(export_filepath, filename)
        w = Workbook()
        ws = w.add_sheet('sheet')
        names = None
        values = []
        for d in data:
            if names is None:
                names = d.keys()
            values.append(d.values())
        for i in range(len(names)):
            ws.write(0, i, names[i])
        for i in range(len(values)):
            for j in range(len(values[i])):
                value = values[i][j]
                if value is None:
                    value = ''
                ws.write(i + 1, j, value)
        w.save(full_filepath)
    except Exception, e:
        logger.warn(e, exc_info=True)
    finally:
        return full_filepath
