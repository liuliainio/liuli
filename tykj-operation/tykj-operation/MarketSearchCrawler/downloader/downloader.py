#-*- coding: utf-8 -*-
'''
Created on Dec 11, 2013

@author: gmliao
'''
import threading
import threadpool
import random
import requests
import urllib2
import os
import datetime
import math

servers = ['10.6.7.100:13000', '10.6.7.200:13000', '10.6.7.169:13000']
_lock = threading.Lock()
BLOCK_SIZE = 1024 * 1024
pool = threadpool.ThreadPool(len(servers) * 3)
finished_blocks = 0
total_blocks = 0
time_start = datetime.datetime.now()


def write_file(path, start, content):
    with _lock:
        if not os.path.exists(path):
            open(path, 'w+').close()
        with open(path, 'r+') as f:
            f.seek(start)
            f.write(content)
            global finished_blocks
            finished_blocks += 1


def left_time():
    now = datetime.datetime.now()
    delta = now - time_start
    seconds = delta.total_seconds()

    def time_str(seconds):
        return '%02d:%02d:%02d' % (math.floor(seconds / (60 * 60)),
                                   math.floor((seconds % (60 * 60)) / 60),
                                   math.floor(seconds % 60),)
    left_seconds = int(seconds * total_blocks / finished_blocks)
    return 'passed_time=%s, left_time=%s' % (time_str(seconds), time_str(left_seconds))


def download_part(url, path, start, length):
    server = servers[random.randint(0, len(servers) - 1)]
    try:
        curl = 'http://%s/xx?url=%s&start=%s&end=%s' % (server, urllib2.quote(url), start, start + length)
        r = requests.get(curl)
        write_file(path, start, r.content)
        print 'successfully download file part. start=%s, length=%s, finished=%s%%, %s' % (start, length, (finished_blocks * 100.0 / total_blocks), left_time())
    except Exception as e:
        print 'error found: %s' % e
        print 'reschedule start: %s, length: %s' % (start, length)
        rs = threadpool.makeRequests(download_part, [((url, path, start, length), {}), ])
        pool.putRequest(rs[0])


def download(url, path):
    r = requests.head(url)
    length = int(r.headers['content-length'])
    r.close()
    global total_blocks
    total_blocks = nblocks = length / BLOCK_SIZE
    args_list = []
    print 'will download [%s] bytes for file: %s, using: block_size=%s, output_file=%s' % (length, url, BLOCK_SIZE, os.path.abspath(path))
    for i in range(nblocks):
        args_list.append(((url, path, i * BLOCK_SIZE, BLOCK_SIZE), {}))
    if length % BLOCK_SIZE != 0:
        total_blocks += 1
        args_list.append(((url, path, nblocks * BLOCK_SIZE, length % BLOCK_SIZE), {}))
    reqs = threadpool.makeRequests(download_part, args_list)
    [pool.putRequest(r) for r in reqs]
    print 'added %s tasks to threadpool' % len(reqs)
    pool.wait()


if __name__ == '__main__':
    import sys
    url = sys.argv[1]
    path = sys.argv[2]
    download(url, path)

