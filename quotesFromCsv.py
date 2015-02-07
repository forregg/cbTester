def loadData(s):

    try:
        res = np.load(s + '.npy')
        print str(datetime.now()) + ' data loaded'
    except IOError:
        data = csv.reader(open(s, 'rb'), delimiter=';')
        dataLists = list()
        for row in data:
            dataLists.append([dparser.parse(row[0]),
                              float(row[1]),
                              float(row[2]),
                              float(row[3]),
                              float(row[4]),
                              float(row[6]),
                              float(row[7]),
                              float(row[8]),
                              float(row[9]),
                              float(row[5]),
                              float(row[10])
                              ])

        res = np.array(dataLists)
        res.dump(s+'.npy')
        print str(datetime.now()) + ' data dumped'
    return res


import csv
from datetime import datetime

import numpy as np
import dateutil.parser as dparser


def to15min(s):
    try:
        data = np.load(s + '.npy')
        print str(datetime.now()) + ' data loaded'
        start = 0
        for row in data:
            if row[0].minute != 0:
                start += 1
                continue
            else:
                break

        newData = []
        i = start
        while 1 == 1:
            if len(data) - i < 15:
                break

            newData.append([
                data[i, 0],
                data[i, 1],
                np.max(data[i : i + 15, 2]), #ebanie [i : i + n] vkluchaut 1-iy elevent, no ne vkluchaut posledniy
                np.min(data[i : i + 15, 3]),
                data[i + 14, 4], #ebanie [i : i + n] vkluchaut 1-iy elevent, no ne vkluchaut posledniy
                data[i, 5],
                np.max(data[i : i + 15, 6]),
                np.min(data[i : i + 15, 7]),
                data[i + 14, 8]])

            i += 15

        res = np.array(newData)
        res.dump(s+'15min.npy')
        print str(datetime.now()) + ' data dumped'

    except IOError:
        print 'io error'
