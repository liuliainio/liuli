import os
import sys
import pickle
import datetime

TMP_FILE = '/tmp/operator.cache'


def save_temp(data):
    old_data = read_temp()
    if old_data:
        for k in data:
            if k not in old_data:
                old_data[k]=data[k]
    else:
        old_data = data
    with open(TMP_FILE, 'wb') as f:
        pickle.dump(old_data, f)
    return old_data


def read_temp():
    data = {}
    try:
        if not os.path.exists(TMP_FILE):
            return data
        with open(TMP_FILE, 'rb') as f:
            data = pickle.load(f)
    except Exception,e:
        print 'error: %s' % e
    finally:
        return data


def load_file(file_path):
    if not os.path.isfile(file_path):
        raise Exception('File:%s is not exists' % file_path)
    line_list = []
    fp = open(file_path, 'r')
    return fp


def parse_operator(line_list):
    operator_dict = {}
    for line in line_list:
        if not line:
            continue
        rows = line.strip().split(',')
        if len(rows) == 2:
            name, imsi = rows
            name = name.strip()
            imsi = imsi.strip()
            if imsi:
                operator_dict[imsi] = name
    return operator_dict


def parse_push_log(line_list):
    push_dict = {}
    for line in line_list:
        if not line:
            continue
        rows = line.strip().split(',')
        if len(rows) == 2:
            clientid, imsi = rows
            clientid = clientid.strip()
            imsi = imsi.strip()
            if imsi and clientid:
                push_dict[imsi] = clientid
    return push_dict


def parse_access_log(line_list):
    access_dict = {}
    for line in line_list:
        if line:
            line = line.strip()
            if line not in access_dict:
                access_dict[line] = 1
            else:
                access_dict[line] += 1
    return access_dict


def meger_operator_clientid(operator_dict, push_dict):
    merged_result = {}
    if not push_dict:
        operator_cache = read_temp()
        if operator_cache:
            return operator_cache
        else:
            raise Exception('Cacahe is null, you should parse push log first.')
    else:
        for imsi in operator_dict:
            if imsi in push_dict:
                clientid = push_dict[imsi]
                merged_result[clientid] = imsi
    cache_combined_result = save_temp(merged_result)
    return cache_combined_result


def print_format(operator_dict, access_dict, clientid_imsi_result):
    for clientid in clientid_imsi_result:
        if clientid in access_dict:
            imsi = clientid_imsi_result[clientid]
            print operator_dict[imsi], access_dict[clientid]



def run(operator_file, access_file, push_file):
    operator_dict = {}
    push_dict = {}
    access_dict = {}
    if operator_file:
        line_list = load_file(operator_file)
        operator_dict = parse_operator(line_list)

    if access_file:
        line_list = load_file(access_file)
        access_dict = parse_access_log(line_list)

    if push_file:
        line_list = load_file(push_file)
        push_dict = parse_push_log(line_list)

    clientid_imsi_result = meger_operator_clientid(operator_dict, push_dict)
    print 'Cached clientid:%s' % len(clientid_imsi_result)
    print_format(operator_dict, access_dict, clientid_imsi_result)

if __name__ == '__main__':
    push_file=access_file=operator_file=''
    if len(sys.argv) == 2:
        operator_file = sys.argv[1]
    elif len(sys.argv) == 3:
        operator_file = sys.argv[1]
        access_file = sys.argv[2]
    elif len(sys.argv) == 4:
        operator_file = sys.argv[1]
        access_file = sys.argv[2]
        push_file = sys.argv[3]
    else:
        print 'usage: xxx.py operator_file_path access_file <opt:push_file_path>'
        sys.exit(2)
    #print operator_file,access_file,push_file
    print '\n%s' % str(datetime.datetime.now())
    run(operator_file, access_file, push_file)
