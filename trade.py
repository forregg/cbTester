# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 16:27:02 2012

@author: Иван
"""
from datetime import date

import numpy as np


def range_months(start, end):
    assert start <= end
    current = start.year * 12 + start.month - 1
    end = end.year * 12 + end.month - 1
    while current <= end:
        yield date(current // 12, current % 12 + 1, 1)
        current += 1


def high(data, currentBarIndex, numberOfBars):
    return np.max(data[(currentBarIndex - numberOfBars + 1) : currentBarIndex, 2])

def low(data, currentBarIndex, numberOfBars):
    return np.min(data[(currentBarIndex - numberOfBars + 1) : currentBarIndex, 3])

def open(data, currentBarIndex, numberOfBars):
    return data[(currentBarIndex - numberOfBars + 1), 1]

def close(data, currentBarIndex, numberOfBars):
    return data[currentBarIndex, 4]

def priceChanel(data, currentBarIndex, numberOfBars):
    return np.array([np.min(data[(currentBarIndex - numberOfBars + 1) : currentBarIndex, 3]),
                     np.max(data[(currentBarIndex - numberOfBars + 1) : currentBarIndex, 2])])

def getRange(data, currentBarIndex, numberOfBars):
    return data[currentBarIndex, 4] - data[(currentBarIndex - numberOfBars + 1), 1]

def getPeriod(data, currentBarIndex, numberOfBars, periodMultiplier):
    bars = range(currentBarIndex - (numberOfBars - 1) * periodMultiplier, currentBarIndex + periodMultiplier, periodMultiplier)
    newData = []
    for i in bars:
        newData.append([
            data[i - periodMultiplier + 1, 0],
            data[i - periodMultiplier + 1, 1],
            np.max(data[i - periodMultiplier + 1 : i, 2]),
            np.min(data[i - periodMultiplier + 1 : i, 3]),
            data[i, 4],
            data[i - periodMultiplier + 1, 5],
            np.max(data[i - periodMultiplier + 1 : i, 6]),
            np.min(data[i - periodMultiplier + 1 : i, 7]),
            data[i, 8]
        ])
    return np.array(newData)

def getBars(data, date1, date2):
    from datetime import datetime
    return np.array([bar for bar in data if date1 <= datetime.date(bar[0]) <= date2])

def getEma(data, currentBarIndex, numberOfBars):
    ema = []
    #get sma first
    sma = np.mean(data[currentBarIndex - numberOfBars + 1: currentBarIndex, 4])
    multiplier = 2 / float(1 + numberOfBars)
    ema.append(sma)

    #EMA(current) = ( (Price(current) - EMA(prev) ) x Multiplier) + EMA(prev)
    ema.append(( (data[currentBarIndex - numberOfBars + 1, 4] - sma) * multiplier) + sma)

    #now calculate the rest of the values
    i = 0
    for barClose in data[currentBarIndex - numberOfBars + 2 : currentBarIndex, 4]:
        tmp = ((barClose - ema[i]) * multiplier) + ema[i]
        i = i + 1
        ema.append(tmp)

    return ema[len(ema)-1]


def atr(data, currentBarIndex, numberOfBars):
    return np.mean(data[(currentBarIndex - numberOfBars + 1) : currentBarIndex, 2] - data[(currentBarIndex - numberOfBars + 1) : currentBarIndex, 3])

def reversionTarget(data, currentBarIndex, numberOfBars):
    range_ = data[currentBarIndex, 4] - data[(currentBarIndex - numberOfBars + 1), 1]
    paths = data[(currentBarIndex - numberOfBars + 1) : currentBarIndex, 1] - data[(currentBarIndex - numberOfBars + 1) : currentBarIndex, 4]
    path = np.sum(np.abs(paths))
    rangeFromPath = path / np.sqrt(numberOfBars)
    delta = np.abs(range_) - rangeFromPath
    if range_ > 0:
        return data[currentBarIndex, 4] - delta

    if range_ < 0:
        return data[currentBarIndex, 4] + delta



def getMarketProfileMax(data):
    #pdb.set_trace()

    min = np.around(np.min(data[:, 3]), 4)
    max = np.around(np.max(data[:, 2]), 4)

    if min == max:
        return 0

    levels = np.arange(min, max, 0.0001)
    mp = np.zeros(levels.size)

    i = 0

    for level in levels:
        for bar in data:
            if bar[2] > level > bar[3]:
                mp[i] = mp[i] + 1
        i = i + 1

        #plt.plot(mp, levels)
        #plt.plot(data[:, 4] )
    #plt.axhline(levels[np.argmax(mp)])
    #plt.show()

    #print levels[np.argmax(mp)]
    return levels[np.argmax(mp)]


def clusterization(data, clastersNum = 2):

    import scipy.cluster.hierarchy as hcluster
    #import pylab
    data = np.array(data)
    #clusters = hcluster.fclusterdata(np.transpose(data), 3, criterion='maxclust', metric='euclidean', depth=1)
    #clusters = hcluster.fclusterdata(data, 2, criterion='maxclust', metric='euclidean', depth=1)
    thresh = 1.5
    clusters = hcluster.fclusterdata(data, thresh, criterion="distance")
    return np.array(clusters)
    #print data
    #print clusters
    #for i in range(len(data[:,0])):
    #    pylab.scatter(data[i,0], data[i,1], c=clusters[i])
    #pylab.axis("equal")
    #pylab.show()
    #pylab.clf()

    

def getInstrumentStat(engine):
    print 'asset growth: ' + str(np.round((engine.data[0].data[len(engine.data[0].data)-1,4]/engine.data[0].data[0,4] - 1) * 100,2))+'%'

def maBid(self, bars):
    return np.sum(bars[:,4])/len(bars)

def getPCWidth(self, pcPeriod = 15 * 12, shift = 0):
    data = self.engine.getHistoryBars(self.engine.data[0].name, pcPeriod, shift)

    if data == []:
        return 0

    lowestLow = np.argmin(data[:, 3])
    pcLow = data[lowestLow, 3]
    highestHigh = np.argmax(data[:, 6])
    pcHigh = data[highestHigh, 6]

    return (pcHigh-pcLow)

def getHistoryVolaByTime(self, startTime, minutes, samples):
    data = self.engine.getHistoryBars(self.engine.data[0].name, samples * 60 * 25, 0)

    if data == []:
        return []

    vola = []
    #s = 0
    for i in range(len(data) - minutes):
        if data[i, 0].minute == startTime[1] and data[i, 0].hour == startTime[0]:
            low = np.min(data[i:i+minutes, 3])
            high = np.max(data[i:i+minutes, 2])
            vola.append(high - low)
            #s += 1
    return vola



def getPCExtremumsBarsNum(self, pcPeriod = 15 * 12, shift = 0):

    data = self.engine.getHistoryBars(self.engine.data[0].name, pcPeriod, shift)

    if data == []:
        return 0

    lowestLow = np.argmin(data[:, 3])
    highestHigh = np.argmax(data[:, 6])

    return [lowestLow,highestHigh]


def pcPeroidSizeDecile(engine, samples, period, bar):
    data = engine.getHistoryBars(engine.data[0].name, (samples + 1) * 24 * 60 + period, 0)
    if len(data) == 0:
        return []
    j = 0
    result = []
    for i in range(len(data)-1):
        if data[len(data) - 1 - i, 0].minute == bar[0].minute and data[len(data) - 1 - i, 0].hour == bar[0].hour:
            if len(data) - 1 - i < period:
                return 0
            result.append(np.max(data[len(data) - 1 - i - period:len(data) - 1 - i,4])-np.min(data[len(data) - 1 - i - period:len(data) - 1 - i,3]))
            j += 1
            if j == samples:
                return result
    return result


def getSamples(engine, samples, startBar, distance):
    data = engine.getHistoryBars(engine.data[0].name, (samples + 3) * 24 * 60, 0)
    if len(data) == 0:
        return []
    j = 0
    result = []

    for i in range(len(data)-1):
        if data[len(data) - 1 - i, 0].minute == startBar[0].minute and data[len(data) - 1 - i, 0].hour == startBar[0].hour:
            if len(data) - 1 - i < distance:
                return 0
            result.append(data[len(data) - 1 - i - distance:len(data) - 1 - i])
            i += distance
            j += 1
            if j == samples:
                return result
    return result

def getVolumeHistory(engine, samples, startBar, distance):
    data = getSamples(engine,samples,startBar,distance)
    result = []
    for sample in data:
        result.append(getVolumeOfBars(sample))

    return result

def distancesBetweenBars(engine, samples, startBar, distance):
    data = engine.getHistoryBars(engine.data[0].name, (samples * 3) * 24 * 60, 0)
    if len(data) == 0:
        return []
    j = 0
    result = []
    for i in range(len(data)-1):
        if data[len(data) - 1 - i, 0].minute == startBar[0].minute and data[len(data) - 1 - i, 0].hour == startBar[0].hour:
            if len(data) - 1 - i < distance:
                return 0
            result.append(data[len(data) - 1 - i - distance,4]-data[len(data) - 1 - i,1])
            j += 1
            if j == samples:
                return result
    return result

def getVolumeOfBars(bars):
    return np.sum(bars[:,9:11])

def getVolumeOfBar(bar):
    return bar[9]+bar[10]

def get15MinVola(self, days = 7):
    data = self.engine.getHistoryBars(self.engine.data[0].name, (days + 1) * 24 * 60, 0)
    stat = np.zeros(24 * 4)

    i = 0
    if data == []:
        return []

    while data[i, 0].hour != 0 and data[i, 0].minute != 0:
        i += 1

    for i in range(i, i+(days * 24 * 60)+15, 15):
        v = np.max(data[i:i+15,2])-np.min(data[i:i+15,3])
        stat[data[i, 0].hour  * 4 + np.round(data[i, 0].minute/15, 0)] += v
    stat /= days
    return stat

def get15minBarNum(time):
    return time.hour*4 + np.round(time.minute/15,0)

def getMarketProfile(engine, period):
    data = engine.getHistoryBars(engine.data[0].name, period, 0)

    if data == [] or len(data) == 0:
        return []
    low = np.min(data[:, 3])
    high = np.max(data[:, 2])

    res = []
    i = low
    while i <= high:
        num = 0
        for j in range(0,len(data)):
            if i >= data[j, 3] and i <= data[j, 2]:
                num += 1
        res.append([i,num])
        i += 0.0001
    return np.array(res)

def getFV(self, period):
    data = self.engine.getHistoryBars(self.engine.data[0].name, period, 0)

    if data == []:
        return 0

    fv = 0

    for i in range(len(data)):
        fv += data[i, 3] + (data[i, 2] - data[i, 3])
    return fv / len(data)

