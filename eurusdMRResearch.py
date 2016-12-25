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
    data = loadData('/home/mage/PycharmProjects/cbTester/data/eurusd_1m_120516.csv')
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

def findMR():
    data = loadData('/home/mage/PycharmProjects/cbTester/data/eurusd_1m_120516.csv_trimmed.csv')

    i = 0
    samples = []
    hours = np.zeros(24)
    for bar in data:
        i = i + 1
        if i < 60*6 or i > len(data) - 60*6:
            continue

        if bar[0].minute not in [29,59]:
            continue

        path = np.max(data[i-60*4:i, 4]) - np.min(data[i-60*4:i, 4])
        delta = np.abs(data[i-60*4, 4]-data[i, 4])
        if path > 0.003 and path < 0.004 and delta < 0.0005:
            samples.append(data[i-60*4:i, 4])
            hours[bar[0].hour] += 1
    print len(samples)
    plt.plot(hours)
    plt.show()
    for s in samples:
        plt.plot(np.array(s))
        plt.show()

def get15minBarNum(bar):
    return bar[0].hour*4 + np.round(bar[0].minute/15,0)

def findLH(years, showRes = True):
    data = loadData('/home/mage/PycharmProjects/cbTester/data/eurusd_1m_120516.csv_trimmed.csv')
    i = 0
    highs = np.zeros(24*4)
    lows = np.zeros(24*4)

    for bar in data:
        i = i + 1
        if i < 60*6 or i > len(data) - 60*6:
            continue

        if bar[0].year not in years:
            continue

        if bar[0].minute not in [14,29,44,59]:
            continue

        interval = data[i-30*6:i+30*2]

        h = np.argmax(interval[:,4])
        l = np.argmin(interval[:,4])

        barh = interval[h]
        barl = interval[l]

        if get15minBarNum(barh) == get15minBarNum(data[i]):
            highs[get15minBarNum(barh)] += 1

        if get15minBarNum(barl) == get15minBarNum(data[i]):
            lows[get15minBarNum(barl)] += 1

    if showRes == True:
        plt.plot(highs, color = 'green')
        plt.plot(lows, color = 'red')
        plt.show()
    else:
        return [highs, lows]

def getBarHLConst():
    hl = []
    years = range(2008,2017)
    resH = []
    resL = []
    for year in years:
        r = findLH([year], False)
        hl.append(r)
    hl = np.array(hl)

    for i in [50]:#range(96):
        highs = []
        lows = []
        for year in range(len(years)):
            highs.append(hl[year,0,i])
            lows.append(hl[year,1,i])
        resH.append(highs)
        resL.append(lows)


    for i in resH:
        print i
        plt.plot(i, label = str(i))
    plt.show()

    for i in resL:
        print i
        plt.plot(i, label = str(i))
    plt.show()

findLH([2013,2014,2015,2016], showRes = True)
getBarHLConst()

#plt.plot(getIntradayHourProfile())
#plt.show()

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


def findLHMonthly(years, barN, showRes = True):
    data = loadData('/home/mage/PycharmProjects/cbTester/data/eurusd_1m_120516.csv_trimmed.csv')
    i = 0

    for bar in data:
        i = i + 1
        if i < 60*6 or i > len(data) - 60*6:
            continue


        if bar[0].minute not in [14,29,44,59]:
            continue

        interval = data[i-30*6:i+30*2]

        h = np.argmax(interval[:,4])
        l = np.argmin(interval[:,4])

        barh = interval[h]
        barl = interval[l]

        if get15minBarNum(barh) == get15minBarNum(data[i]):
            highs[get15minBarNum(barh)] += 1

        if get15minBarNum(barl) == get15minBarNum(data[i]):
            lows[get15minBarNum(barl)] += 1

    if showRes == True:
        plt.plot(highs, color = 'green')
        plt.plot(lows, color = 'red')
        plt.show()
    else:
        return [highs, lows]



