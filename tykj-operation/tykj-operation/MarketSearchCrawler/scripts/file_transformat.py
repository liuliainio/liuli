import re
import sys
file = sys.argv[1]
f = open('%s' % file, 'r')
w = open('%s.2' % file, 'w')
for line in f.readlines():
    if 'to_date(' in line:
        line = line.split(',')
        for i in range(len(line)):
            line[i] = line[i].replace('dd-mm-yyyy', '%Y-%m-%d')
            line[i] = line[i].replace('hh24:mi:ss', '%H:%m:%s')
            if 'to_date(' in line[i]:
                time = line[i].split("to_date('")[1].split("'")[0].split(' ')[0]
                time = time.split('-')[2] + '-' + time.split('-')[1] + '-' + time.split('-')[0]
                line[i] = line[i].replace('to_date(', 'date_format(')
                pattern_string = '[0-9]{2}-[0-9]{2}-[0-9]{4}'
                pattern = re.compile(pattern_string)
                match = pattern.search(line[i])
                line[i] = line[i].replace(match.group(), time)
        line = ','.join(line)
    w.write(line)
