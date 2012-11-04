import numpy as np
import dateutil.parser as dparser
import csv
from datetime import datetime

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
                              float(row[9])])

        res = np.array(dataLists)
        res.dump(s+'.npy')
        print str(datetime.now()) + ' data dumped'
    return res