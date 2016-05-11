import csv
from datetime import datetime
from datetime import timedelta

import numpy as np
import dateutil.parser as dparser


def loadData(s):

    try:
        res = np.load(s + '.npy')
        print str(datetime.now()) + ' data loaded'
    except IOError:
        data = csv.reader(open(s, 'rb'), delimiter=',')
        dataLists = list()
        for row in data:

            hours = timedelta(0, int(row[1][0]+row[1][1]) * 3600)
            minutes = timedelta(0, int(row[1][2]+row[1][3]) * 60)
            seconds = timedelta(0, int(row[1][4]+row[1][5]))
            time = hours + minutes + seconds + dparser.parse(row[0])

            dataLists.append([
                time,
                float(row[2]),
                float(row[3]),
                float(row[4]),
                float(row[5]),
                float(row[6]),
                float(row[7]),
                float(row[8]),
                float(row[9]),
                float(row[10]),
                float(row[11]),
                float(row[12])
            ])

        res = np.array(dataLists)
        res.dump(s+'.npy')
        print str(datetime.now()) + ' data dumped'
    return res

def loadDataRts(s):

    startDate = 0
    endDate = 0
    firstBar = 0

    try:
        res = np.load(s + '.npy')
        print str(datetime.now()) + ' data loaded'
    except IOError:
        data = csv.reader(open(s, 'rb'), delimiter=',')
        dataLists = list()

        for row in data:

            hours = timedelta(0, int(row[1][0]+row[1][1]) * 3600)
            minutes = timedelta(0, int(row[1][2]+row[1][3]) * 60)
            seconds = timedelta(0, int(row[1][4]+row[1][5]))
            time = hours + minutes + seconds + dparser.parse(row[0])

            dataLists.append([
                time,
                float(row[2]),
                float(row[3]),
                float(row[4]),
                float(row[5]),
                float(row[6])
            ])

        res = np.array(dataLists)
        res.dump(s+'.npy')
        print str(datetime.now()) + ' data dumped'
    return res