from matplotlib import pyplot as plt
import numpy as np
from datetime import *

from quotesFromCsv import loadData
from forexSessions import *


def getAverageSpread():
    data = loadData('/home/mage/PycharmProjects/cbTester/data/gbpusd_10sec_upto06052016.csv')
    spread = np.zeros(24)
    spreadCount = np.zeros(24)
    i = 0
    for bar in data:
        i = i + 1
        if i < 60*6:
            continue

        if bar[0].minute not in [59]:
            continue
        spread[bar[0].hour] += bar[9]-bar[4]
        spreadCount[bar[0].hour] += 1

    for i in xrange(len(spread)):
        spread[i] /= spreadCount[i]

    return spread


def getIntradayHourProfile():
    data = loadData('home/mage/PycharmProjects/cbTester/data/eurusd_10sec_110516.csv')
    vola = np.zeros(24)
    volaCount = np.zeros(24)
    i = 0
    for bar in data:
        i = i + 1
        if i < 60*6:
            continue

        if bar[0].minute not in [59]:
            continue
        vola[bar[0].hour] += np.abs(np.max(data[i-60*6:i, 2]) - np.min(data[i-60*6:i, 3]))
        volaCount[bar[0].hour] += 1

    print volaCount
    for i in xrange(len(vola)):
        vola[i] /= volaCount[i]

    return vola


def test():
    data = loadData('/home/mage/PycharmProjects/cbTester/data/eurusd_1sec_upto06052016.csv')
    res = []
    for bar in data:
        if bar[0].day == 21 and bar[0].year == 2016 and bar[0].month == 4 and bar[0].hour == 15:
            print bar[0]
            print bar[0].utcoffset()
            res.append(bar)
    return res


from matplotlib.finance import candlestick
from matplotlib.pyplot import *

def quotesToCandlestick(data):
    from matplotlib.dates import date2num
    #result = [data[:,0],data[:,1],data[:,4],data[:,2],data[:,3]]
    return np.column_stack((date2num(data[:,0]),data[:,1],data[:,4],data[:,2],data[:,3]))


def findStik():
    data = loadData('/home/mage/PycharmProjects/cbTester/data/eurusd_10sec_110516.csv')
    path = np.zeros(60*6-2)
    i = 0
    count = 0
    for bar in data:
        i = i + 1
        if i < 60*6:
            continue

        if bar[0].minute not in [00]:
            continue
        if bar[0].second not in [10]:
            continue

        if bar[4] - bar[1] > 0.0005:
            path += data[i-60*6:i-2, 4]
            r = np.max(data[i-60*6:i-2, 4]) - np.min(data[i-60*6:i-2, 4])
            print r
            path -= data[i-60*6, 4]
            count += 1
            print bar[0]

    path /= count
    range = path[60*6-3]-path[0]
    print range
    plot(path)
    show()



findStik()
exit()


res = test()
res = np.array(res)
print res
fig = figure()
fig.subplots_adjust(bottom=0.2)
ax = fig.add_subplot(111)
data = quotesToCandlestick(res)
candlestick(ax, data, width=0.00006, colorup='g', colordown='r')
ax.autoscale_view()

show()
