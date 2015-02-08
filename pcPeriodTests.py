from quotesFromCsv import loadData
from matplotlib import pyplot as plt
import numpy as np

from quotesFromCsv import to15min
from forexSessions import *
data = loadData('c:\\eurusd_1m.csv15min')

#to15min('c:\\eurusd_1m.csv')

def get15minBarNum(time):
    return time.hour*4 + np.round(time.minute/15,0)

def getMaxMinBars(window = 8, years = 0, summerTime = 777):
    res = np.zeros(96)
    for i in range(window, len(data) - window):
        if years != 0:
            if data[i,0].year not in years:
                continue

        if summerTime != 777:
            if summerTime is True:
                if forexSessions.isSummerTimeInLondon(data[i,0]) is not True:
                    continue
            else:
                if forexSessions.isSummerTimeInLondon(data[i,0]) is True:
                    continue
        if np.argmax(data[i-window:i+window, 2]) == window:
            res[get15minBarNum(data[i,0])] +=1
        if np.argmin(data[i-window:i+window, 3]) == window:
            res[get15minBarNum(data[i,0])] +=1
    return res

def plotMaxMinBars():
    window = 24
    mmSummer = getMaxMinBars(years=[2012,2013], summerTime = True, window=window)
    mmWinter = getMaxMinBars(years=[2012,2013], summerTime = False, window=window)
    mmSummer = np.array(mmSummer) / np.max(mmSummer)
    mmWinter = np.array(mmWinter) / np.max(mmWinter)
    plt.plot(mmSummer, label = '15min bar*'+str(window*2+1)+' extremums summer')
    plt.plot(mmWinter, label = '15min bar*'+str(window*2+1)+' extremums winter')
    plt.legend(loc = 'best')
    plt.grid()
    plt.show()

def getPathAndDistance(data, holdBars, years = 0, trade15MinBars = 0, timeStamp = True, summerTime = 777):
    result = []
    for i in range(0, len(data) - holdBars):
        if years != 0:
            if data[i,0].year not in years:
                continue
        if trade15MinBars != 0:
            if get15minBarNum(data[i,0]) not in trade15MinBars:
                continue
        if summerTime != 777:
            if summerTime is True:
                if forexSessions.isSummerTimeInLondon(data[i,0]) is not True:
                    continue
            else:
                if forexSessions.isSummerTimeInLondon(data[i,0]) is True:
                    continue


        path = abs(data[i+holdBars-1, 4] - data[i, 1])
        distance = 0
        for j in range(i, i+holdBars):
            distance += abs(data[j, 4] - data[j, 1])
        if timeStamp:
            result.append([distance, path, data[i, 0].hour * 4+data[i, 0].minute/15])
        else:
            result.append([distance, path])
    return result

def getPathAndDistanceBackward(data, holdBars, years = 0, trade15MinBars = 0, timeStamp = True, summerTime = 777):
    result = []
    for i in range(0 + holdBars, len(data)):
        if years != 0:
            if data[i,0].year not in years:
                continue
        if trade15MinBars != 0:
            if get15minBarNum(data[i,0]) not in trade15MinBars:
                continue
        if summerTime != 777:
            if summerTime is True:
                if forexSessions.isSummerTimeInLondon(data[i,0]) is not True:
                    continue
            else:
                if forexSessions.isSummerTimeInLondon(data[i,0]) is True:
                    continue


        path = abs(data[i-(holdBars-1), 1] - data[i, 4])
        distance = 0
        for j in range(i-(holdBars-1), i+1):
            distance += abs(data[j, 4] - data[j, 1])
        if timeStamp:
            result.append([distance, path, data[i, 0].hour * 4+data[i, 0].minute/15])
        else:
            result.append([distance, path])
    return result


def calcMaxMinRevTimeForEach15minBar():
    startYear = 2012
    endYear = 2013

    maxMRSummer = []
    maxMRHoldBarsSummer = []
    for barNum in range(0,96):
        finRes = []
        for i in range(2,17):
            res = getPathAndDistance(data, i, years = range(startYear, endYear+1,1), trade15MinBars = [barNum],summerTime=True)
            res = np.array(res)
            res = np.mean(res[:, 0])/np.mean(res[:, 1])/np.sqrt(i)
            finRes.append(res)
        print 'summer: '+str(barNum)+": "+str(np.argmax(finRes)+2)+": "+str(np.max(finRes))
        maxMRSummer.append(np.max(finRes))
        maxMRHoldBarsSummer.append(np.argmax(finRes)+2)

    maxMRWinter = []
    maxMRHoldBarsWinter = []
    for barNum in range(0,96):
        finRes = []
        for i in range(2,17):
            res = getPathAndDistance(data, i, years = range(startYear, endYear+1,1), trade15MinBars = [barNum],summerTime=False)
            res = np.array(res)
            res = np.mean(res[:, 0])/np.mean(res[:, 1])/np.sqrt(i)
            finRes.append(res)
        print 'winter: '+str(barNum)+": "+str(np.argmax(finRes)+2)+": "+str(np.max(finRes))
        maxMRWinter.append(np.max(finRes))
        maxMRHoldBarsWinter.append(np.argmax(finRes)+2)

    plt.plot(maxMRWinter, label = 'maxMR winter')
    plt.plot(maxMRSummer, label = 'maxMR summer')
    plt.legend(loc = 'best')
    plt.grid()
    plt.show()
    plt.plot(maxMRHoldBarsWinter, label = 'maxMRHoldBars winter')
    plt.plot(maxMRHoldBarsSummer, label = 'maxMRHoldBars summer')
    plt.legend(loc = 'best')
    plt.grid()
    plt.show()



def getMRByTime(years = range(2008,2014), holdBars = 8, summerTime = 777):
    pd = getPathAndDistance(data, holdBars, years = years, summerTime=summerTime)
    pd = np.array(pd)
    mr = np.zeros(96)
    mrStdDev = np.zeros(96)

    for barNum in range(0,96):
        pdBarNum = pd[pd[:,2]==barNum]
        mr[barNum] = np.mean(pdBarNum[:,0])/np.mean(pdBarNum[:,1])/np.sqrt(holdBars)
    return mr

def getPathAndDistByTime(years = range(2008,2014), holdBars = 8, summerTime = 777):
    pd = getPathAndDistance(data, holdBars, years = years, summerTime=summerTime)
    pd = np.array(pd)
    p = np.zeros(96)
    d = np.zeros(96)

    for barNum in range(0,96):
        pdBarNum = pd[pd[:,2]==barNum]
        p[barNum] = np.mean(pdBarNum[:,0])
        d[barNum] = np.mean(pdBarNum[:,1])
    return [p, d]


def whatChanged():
    mrSummer = getMRByTime([2012,2013],8,summerTime=True)
    mrWinter = getMRByTime([2012,2013],8,summerTime=False)
    mrOldSummer = getMRByTime(range(2008,2012),8,summerTime=True)
    mrOldWinter = getMRByTime(range(2008,2012),8,summerTime=False)

    plt.plot(mrOldSummer,label='mr old summer')
    plt.plot(mrSummer,label='mr 2012,2013 summer')
    plt.legend(loc = 'best')
    plt.show()
    plt.plot(mrOldWinter,label='mr old winter')
    plt.plot(mrWinter,label='mr 2012,2013 winter')
    plt.legend(loc = 'best')
    plt.show()

    pdSummer = getPathAndDistByTime([2012,2013],8,summerTime=True)
    pdWinter = getPathAndDistByTime([2012,2013],8,summerTime=False)
    pdOldSummer = getPathAndDistByTime(range(2008,2012),8,summerTime=True)
    pdOldWinter = getPathAndDistByTime(range(2008,2012),8,summerTime=False)

    plt.plot(pdOldSummer[0],label='p old summer')
    plt.plot(pdSummer[0],label='p 2012,2013 summer')
    plt.plot(pdOldSummer[1],label='d old summer')
    plt.plot(pdSummer[1],label='d 2012,2013 summer')
    plt.legend(loc = 'best')
    plt.show()
    plt.plot(pdOldWinter[0],label='p old winter')
    plt.plot(pdWinter[0],label='p 2012,2013 winter')
    plt.plot(pdOldWinter[1],label='d old winter')
    plt.plot(pdWinter[1],label='d 2012,2013 winter')
    plt.legend(loc = 'best')
    plt.show()



def barChartOfMrByYear():
    years = range(2010,2014)

    for holdBars in range(4,24,4):
        for year in years:
            x = range(0,96)
            x = np.array(x)
            x *= len(years)+3
            x += (year - years[0])
            y = getMRByTime([year],holdBars,summerTime=True)
            y = np.array(y) - 1
            print str(holdBars) + ': ' + str(np.mean(y))
            plt.bar(x, y)
        plt.grid()
        plt.show()

#barChartOfMrByYear()
#plotMaxMinBars()
#calcMaxMinRevTimeForEach15minBar()

#whatChanged()