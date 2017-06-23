# encoding=utf8
import os
import sys


def start(file, path):
    o = open(file, 'r')
    img_dic = {}
    if 'icon' in file:
        for line in o.readlines():
            key = line.strip().split('/')[-1]
            value = line.strip()
            img_dic[key] = value
    else:
        for line in o.readlines():
            for l in line.strip().split(' '):
                key = l.strip().split('/')[-1]
                value = l.strip()
                img_dic[key] = value
    for name in os.listdir(path):
        if name in img_dic:
            command_str = "cp %s/%s /mnt/ctappstore/vol2/%s" % (path, name, img_dic[name])
            print command_str
            print os.popen(command_str).read()

if __name__ == "__main__":
    start(sys.argv[1], sys.argv[2])
