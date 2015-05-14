from datetime import date
import matplotlib.pyplot as plt
import numpy as np
from quotesFromCsv import loadData
from tester import Tester
from instrument import Instrument
from strategy import Strategy
from order import Order
import calendar
from forexSessions import *

from trade import *
from ma import ema

import quotesFromDS
#from quotesFromCsv import to15min
#loadData('c:\\pairs\\eurusd_1m.csv')
#to15min('c:\\pairs\\eurusd_1m.csv')


startTest = date(2010, 1, 1)
stopTest = date(2010, 10, 10)

gbpusd = loadData('/home/mage/PycharmProjects/cbTester/data/g.csv')
eurusd = loadData('/home/mage/PycharmProjects/cbTester/data/e.csv')



class PairMeanRev(Strategy):
#params

    def __init__(self, engine, params):
        self.engine = engine
        self.lotSizeInUSD = 1000000
        self.commissionPerPip = self.lotSizeInUSD / 1000000 * 25
        self.result = []
        #self.pOpt = params['pOpt']
        self.pOptimization = params['pOptimization']
        self.queue = []
        self.queueClose = []

    def onBar(self, bar):

        for o in self.queue:
            if bar[11] == o[0]:
                self.engine.sendOrder(Order(o[1], 0, 0, 0, 1, 0, 110, market=True, instrument=o[0]), bar)
                self.queue.remove(o)

        for p in reversed(self.queueClose):
            if bar[11] == p.order.instrument:
                if p in self.engine.getPositions():
                    self.engine.closePosition(p, bar, market=True)
                self.queueClose.remove(p)


        filters = 0

        if filters:
            if get15minBarNum(bar[0]) in [47,48]:#range(29, 43):
                return

            #if forexSessions.isSummerTimeInLondon(bar[0]) is False:
            #    return

            """if forexSessions.isSummerTimeInLondon(bar[0]) is False and get15minBarNum(bar[0]) not in [26,28,33,36,38,42,43,49,51,53,55,59,62,63,64,83,86,87,90]:
                return

            if forexSessions.isSummerTimeInLondon(bar[0]) is True and get15minBarNum(bar[0]) not in [20,29,30,31,34,35,37,40,42,44,47,49,51,52,56,58,59,60,73]:
                return
            """
            dow = calendar.weekday(bar[0].year, bar[0].month, bar[0].day)
            if dow not in [0,1,3,4,5,6]:
                return


        e = self.engine.getHistoryBars(self.engine.data[0].name, 2 * 60, 0)
        g = self.engine.getHistoryBars(self.engine.data[1].name, 2 * 60, 0)
        if e == []:
            return
        if g == []:
            return

        pcHighE = np.max(e[:, 6])
        pcLowE = np.min(e[:, 3])
        pcHighG = np.max(g[:, 6])
        pcLowG = np.min(g[:, 3])

        if pcHighE == pcLowE or pcHighG == pcLowG:
            return

        pe = (e[len(e) - 1, 4] - pcLowE)/(pcHighE - pcLowE)
        pg = (g[len(g) - 1, 4] - pcLowG)/(pcHighG - pcLowG)

        r = pe-pg
        positions = self.engine.getPositions()

        if len(positions) > 0:
            profit = 0
            for p in reversed(positions):
                profit += (self.engine.getHistoryBars(p.order.instrument, 1, 0)[0, 4] - p.order.price) * p.order.orderType * self.lotSizeInUSD - self.commissionPerPip

            if profit > 1500:
                for p in reversed(positions):
                    if p not in self.queueClose:
                        self.queueClose.append(p)

        if len(positions) == 0:
            if r > 0.7:
                if bar[11] == "eurusd":
                    self.engine.sendOrder(Order(1, 0, 0, 0, 1, 0, 60, market=True, instrument="eurusd"), bar)
                    self.queue.append(["gbpusd", -1])
                if bar[11] == "gbpusd":
                    self.engine.sendOrder(Order(-1, 0, 0, 0, 1, 0, 60, market=True, instrument="gbpusd"), bar)
                    self.queue.append(["eurusd", 1])
            """if r < -0.75:
                if bar[11] == "eurusd":
                    self.engine.sendOrder(Order(-1, 0, 0, 0, 1, 0, 110, market=True, instrument="eurusd"), bar)
                    self.queue.append(["gbpusd", 1])
                if bar[11] == "gbpusd":
                    self.engine.sendOrder(Order(1, 0, 0, 0, 1, 0, 110, market=True, instrument="gbpusd"), bar)
                    self.queue.append(["eurusd", -1])"""

        """
        if len(positions) == 2:
            if r > 0.95:
                if bar[11] == "eurusd":
                    self.engine.sendOrder(Order(1, 0, 0, 0, 1, 0, 60, market=True, instrument="eurusd"), bar)
                    self.queue.append(["gbpusd", -1])
                if bar[11] == "gbpusd":
                    self.engine.sendOrder(Order(-1, 0, 0, 0, 1, 0, 60, market=True, instrument="gbpusd"), bar)
                    self.queue.append(["eurusd", 1])
            if r < -0.9:
                if bar[11] == "eurusd":
                    self.engine.sendOrder(Order(-1, 0, 0, 0, 1, 0, 60, market=True, instrument="eurusd"), bar)
                    self.queue.append(["gbpusd", 1])
                if bar[11] == "gbpusd":
                    self.engine.sendOrder(Order(1, 0, 0, 0, 1, 0, 60, market=True, instrument="gbpusd"), bar)
                    self.queue.append(["eurusd", -1])
        """
        """
        if len(positions) >= 1:
            for p in reversed(positions):
                if r > -0.2:
                    if p.order.instrument == "eurusd" and bar[11] == "eurusd" and p.order.orderType == -1:
                        self.engine.closePosition(p, bar, market=True)
                    if p.order.instrument == "gbpusd" and bar[11] == "gbpusd" and p.order.orderType == 1:
                        self.engine.closePosition(p, bar, market=True)
                if r < 0.2:
                    if p.order.instrument == "eurusd" and bar[11] == "eurusd" and p.order.orderType == 1:
                        self.engine.closePosition(p, bar, market=True)
                    if p.order.instrument == "gbpusd" and bar[11] == "gbpusd" and p.order.orderType == -1:
                        self.engine.closePosition(p, bar, market=True)

        """
        self.result.append(r)

    def onStop(self):
        if self.pOptimization is False:
            self.engine.generateTextReport(self.lotSizeInUSD, self.commissionPerPip)
            self.engine.printTrades(self.lotSizeInUSD, self.commissionPerPip)
            self.engine.showEquity(self.lotSizeInUSD, self.commissionPerPip)
            self.engine.getFilterAnalyze(self.lotSizeInUSD, self.commissionPerPip)
            self.engine.getMonthlyReturns(self.lotSizeInUSD, self.commissionPerPip)
            self.engine.getProfitsByDayOfWeek(self.lotSizeInUSD, self.commissionPerPip)
            self.engine.getProfitsByTimeOfDay(self.lotSizeInUSD, self.commissionPerPip)
            self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1)
            import matplotlib.pyplot as plt
            plt.plot(self.result)
            plt.show()
        else:
            self.engine.generateTextReport(self.lotSizeInUSD, self.commissionPerPip)


    def onGetStatOnPositionOpen(self, position, bar):
        e = self.engine.getHistoryBars(self.engine.data[0].name, 2 * 60, 0)
        g = self.engine.getHistoryBars(self.engine.data[1].name, 2 * 60, 0)
        if e == []:
            return
        if g == []:
            return

        pcHighE = np.max(e[:, 6])
        pcLowE = np.min(e[:, 3])
        pcHighG = np.max(g[:, 6])
        pcLowG = np.min(g[:, 3])

        if pcHighE == pcLowE or pcHighG == pcLowG:
            return

        pe = (e[len(e) - 1, 4] - pcLowE)/(pcHighE - pcLowE)
        pg = (g[len(g) - 1, 4] - pcLowG)/(pcHighG - pcLowG)

        r = pe-pg

        return pg

    def onGetStatOnPositionClose(self, position, bar):
        e = self.engine.getHistoryBars("eurusd", 110, 0)
        g = self.engine.getHistoryBars("gbpusd", 110, 0)
        r = e[:, 1:5] - g[:, 1:5]
        r = np.hstack((np.zeros((len(r), 1)),r))
        return r

#for opt in range(1,5):
#    tester = Tester([Instrument('eurusd', eurusd), Instrument('gbpusd', gbpusd)], PairMeanRev, {'pOptimization': True, 'pOpt':opt}, True)
tester = Tester([Instrument('eurusd', eurusd), Instrument('gbpusd', gbpusd)], PairMeanRev, {'pOptimization': False}, True)


"""
def getPL(pair1data, pair2data, emaPeriod = 100, signalLevel = 2.5, signalCloseLevel = 0, tradeCosts = 0.0004):


    pair1 = pair1data[:, 4]
    pair2 = pair2data[:, 4]

    strategyParams = {'pOptimization': False}
    tester = Tester([Instrument('eurusd', data)], Break20, strategyParams, True)


    pf = []
    p = []
    profits = []
    stat = []
    pair1OpenPrice = 0
    pair2OpenPrice = 0
    pair1ClosePrice = 0
    pair2ClosePrice = 0
    inPosS = False
    inPosL = False

    period = emaPeriod
    pair1Normalized = []
    e1 = []
    s1 = []

    for i in range(0, len(pair1)):
        if i < period + 1:
            ema1 = pair1[i]
            std1 = np.std(pair1[0:period])
        else:
            ema1 = ema(pair1[i-period-1:i], period)[1]
            std1 = np.std(pair1[i-period:i])
        e1.append(ema1)
        s1.append(std1)
        pair1Normalized.append((pair1[i]-ema1)/std1)


    pair2Normalized = []
    e2 = []
    s2 = []
    for i in range(0, len(pair2)):
        if i < period + 1:
            ema2 = pair2[i]
            std2 = np.std(pair2[0:period])
        else:
            ema2 = ema(pair2[i-period-1:i], period)[1]
            std2 = np.std(pair2[i-period:i])

        e2.append(ema2)
        s2.append(std2)
        pair2Normalized.append((pair2[i]-ema2)/std2)

    spread = np.array(pair1Normalized)- np.array(pair2Normalized)



    for i in range(0, len(spread)):
        if inPosS == False and spread[i] > signalLevel:# and pair1data[i, 0].hour == opt:
            inPosS = True
            start = i
            pair1OpenPrice = pair1[i]#pair1data[i, 4]
            pair2OpenPrice = pair2[i]#pair2data[i, 8]
            #plt.plot(pair1[start:i]-pair1[start], color = 'red')
            #plt.plot(pair2[start:i]-pair2[start], color = 'green')
            #plt.plot(spread[start:i], color = 'black')
            #plt.show()

            #print 'p1 ' + str(pair1OpenPrice) + '-' + str(pair1ClosePrice) + ' = ' + str(pair1OpenPrice - pair1ClosePrice)
            #print 'p2 ' + str(pair2ClosePrice) + '-' + str(pair2OpenPrice) + ' = ' + str(pair2ClosePrice - pair2OpenPrice)

        if inPosS == True and spread[i] < -signalCloseLevel:
            inPosS = False
            pair1ClosePrice = pair1[i]#pair1data[i, 8]
            pair2ClosePrice = pair2[i]#pair2data[i, 4]
            stat.append(pair1data[i, 0].hour)
            profits.append(-(pair1ClosePrice - pair1OpenPrice)/pair1OpenPrice + (pair2ClosePrice - pair2OpenPrice)/pair2OpenPrice-tradeCosts)

        if inPosL == False and spread[i] < -signalLevel:# and pair1data[i, 0].hour == opt:
            inPosL = True
            start = i
            pair1OpenPrice = pair1[i]#pair1data[i, 8]
            pair2OpenPrice = pair2[i]#pair2data[i, 4]

        if inPosL == True and spread[i] > signalCloseLevel:
            inPosL = False
            pair1ClosePrice = pair1[i]#pair1data[i, 4]
            pair2ClosePrice = pair2[i]#pair2data[i, 8]
            stat.append(pair1data[i, 0].hour)
            profits.append((pair1ClosePrice - pair1OpenPrice)/pair1OpenPrice - (pair2ClosePrice - pair2OpenPrice)/pair2OpenPrice-tradeCosts)
            #print (-(pair1ClosePrice - pair1OpenPrice) + (pair2ClosePrice - pair2OpenPrice)-tradeCosts)
            #plt.plot(pair1[i-(i-start):i]-pair1[i], color = 'red')
            #plt.plot(pair2[i-(i-start):i]-pair2[i], color = 'green')
            #plt.show()
        i += 1

    #print profits
    #plt.plot(np.cumsum(profits))
    #plt.show()
    #if optimization == 0:
    #    plt.plot(np.cumsum(profits))
    #   plt.show()
    profits = np.array(profits)
    if np.sum(profits[profits<0]) != 0:
        pf = -np.sum(profits[profits>0])/np.sum(profits[profits<0])
    #else: pf.append(0)
    #p.append(np.sum(profits))
    print 'pf: '+str(pf)
    print 'mo: '+str(np.mean(profits))
    return [profits, stat]

    #if optimization == 1:
    #    plt.plot(pf)
    #    plt.show(pf)
    #    plt.plot(p)
    #    plt.show(p)
    #plt.plot(spread)
    #plt.plot(pair2Normalized)
    #plt.plot(pair2Normalized - pair1Normalized, color = 'red')

    #plt.show()

#for opt in range(100, 1000, 100):

argh = []
res, stat = getPL(pair1data, pair2data, emaPeriod=12, signalLevel=2, signalCloseLevel=0, tradeCosts=0)#.0003)
plt.plot(np.cumsum(res))
plt.show()
for i in range(0, 24):
    argh.append(np.sum(res[np.array(stat)==i]))

argh = np.array(argh)

print argh>0
plt.plot(argh)
plt.show()

"""