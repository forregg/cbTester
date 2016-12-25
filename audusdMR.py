from strategy import Strategy
from order import Order
from position import Position
from trade import *
from datetime import timedelta, datetime
import matplotlib.pyplot as plt
from forexSessions import *
from scipy import stats
import calendar
from datetime import timedelta
class MR(Strategy):
#params

    def __init__(self, engine, params):
        self.name = 'eurusdmr'
        self.engine = engine
        self.lotSizeInUSD = 1000000
        self.commissionPerPip = self.lotSizeInUSD / 1000000 * 25
        self.pOptimization = False
        if params != None:
            if 'pOptimization' in params:
                self.pOptimization = params['pOptimization']
            if 'pOpt' in params:
                self.pOpt = params['pOpt']

        getInstrumentStat(engine)

    def onStart(self):
        """not implemented yet"""


    def getDailyVola(self, currentBar, samples = 30):
        data = self.engine.getHistoryBars(self.engine.data[0].name, 60 * 24 * (samples + 2), 0)
        if data == []:
            return

        vola = []

        for i in range(samples):
            h = np.max(data[len(data)-1 - ((i + 1) * 24 * 60) : len(data)-1 - (i * 24 * 60),2])
            l = np.min(data[len(data)-1 - ((i + 1) * 24 * 60) : len(data)-1 - (i * 24 * 60),3])
            vola.append(h-l)

        return vola

    def getPercentileOfDailyVola(self, currentBar, samples = 30):

        vola = self.getDailyVola(currentBar, samples)

        data = self.engine.getHistoryBars(self.engine.data[0].name, 24 * 60, 0)
        if data == []:
            return

        pcHigh = np.max(data[:, 2])
        pcLow = np.min(data[:, 3])

        lastDayVola = pcHigh-pcLow

        return stats.percentileofscore(vola, lastDayVola)



    def getDailyRangeVola(self, barsNum, samples = 30):
        data = self.engine.getHistoryBars(self.engine.data[0].name, 60 * 24 * (samples + 2), 0)
        if data == []:
            return

        vola = []

        for i in range(samples):
            h = np.max(data[len(data)-1 - (i * 24 * 60) - barsNum : len(data)-1 - (i * 24 * 60),2])
            l = np.min(data[len(data)-1 - (i * 24 * 60) - barsNum : len(data)-1 - (i * 24 * 60),3])
            vola.append(h-l)

        return vola

    def getPercentileOfDailyRangeVola(self,barsNum, samples = 30):

        vola = self.getDailyRangeVola(barsNum, samples)

        data = self.engine.getHistoryBars(self.engine.data[0].name, barsNum, 0)
        if data == []:
            return

        pcHigh = np.max(data[:, 2])
        pcLow = np.min(data[:, 3])

        lastRangeVola = pcHigh-pcLow

        return stats.percentileofscore(vola, lastRangeVola)



    def onGetStatOnPositionOpen(self, position, bar):
        return self.getPercentileOfDailyRangeVola(180)

        #return self.engine.getHistoryBars(self.engine.data[0].name, 180, 0)


    def onGetStatOnPositionClose(self, position, bar):
        return self.engine.getHistoryBars(self.engine.data[0].name, 60, 0)

    def onBar(self, bar):

        if bar[0].year not in [2012,2013,2014,2015,2016]:
            return


        #positions = self.engine.getPositions()
        #if len(positions) > 0:
        #    for p in reversed(positions):
        #        if get15minBarNum(bar[0]) in [14]:
        #        #if bar[0].hour == 4 and bar[0].minute == 29:
        #            self.engine.closePosition(p, bar)


        positionTimeStop = 60 * 60 * 15.5
        positionTimeStop = timedelta(seconds=positionTimeStop)

        positionTimeStopShort = 60 * 60 * 15.5
        positionTimeStopShort = timedelta(seconds=positionTimeStopShort)

        positions = self.engine.getPositions()
        if len(positions) > 0:
            for p in reversed(positions):
                if p.order.orderType == 1:
                    if p.openTime + positionTimeStop <= bar[0]:
                        self.engine.closePosition(p, bar)
                else:
                    if p.openTime + positionTimeStopShort <= bar[0]:
                        self.engine.closePosition(p, bar)

        #positionTimeStopShort = 15 * 60
        #positionTimeStopShort = timedelta(seconds=positionTimeStopShort)


        #positions = self.engine.getPositions()
        #if len(positions) > 0:
        #    for p in reversed(positions):
        #        if p.openTime + positionTimeStopShort <= bar[0]:
        #            profit = (bar[4] - p.order.price) * p.order.orderType * self.lotSizeInUSD - self.commissionPerPip
        #            if profit < 0:
        #                self.engine.closePosition(p, bar)

        #if forexSessions.isSummerTimeInLondon(bar[0]) is False:
        #    return


        if get15minBarNum(bar[0]) not in [94]:#range(23,28):
            return

        if bar[0].minute not in [14,29,44,59]:#range(0,60,5)
            return

        data = self.engine.getHistoryBars(self.engine.data[0].name, 180, 0)
        if data == []:
            return
        pcHigh = np.max(data[:, 7])
        pcLow = np.min(data[:, 3])


        perc = (bar[4]- pcLow)/ (pcHigh - pcLow)

        data = self.engine.getHistoryBars(self.engine.data[0].name, 60 * 24, 0)
        if data == []:
            return
        pcHigh = np.max(data[:, 7])
        pcLow = np.min(data[:, 3])

        lastDayVola = pcHigh-pcLow

        data = self.engine.getHistoryBars(self.engine.data[0].name, 60 * 3, 0)
        if data == []:
            return
        pcHigh = np.max(data[:, 7])
        pcLow = np.min(data[:, 3])

        last3HVola = pcHigh-pcLow


        v = last3HVola / lastDayVola


        #if last3HVola < 0.003:
        #    return

        dailyVolaPercentile = self.getPercentileOfDailyVola(bar)

        #if self.getPercentileOfDailyRangeVola(60) < 70:
        #    return

        #if dailyVolaPercentile > 67 or dailyVolaPercentile < 10:
        #    return

        if self.getPercentileOfDailyRangeVola(180) < 85:
            return

        if perc > 0.7:
            #if v < 0.3:
            self.engine.sendOrder(Order(bar[11], -1, 0, 0, 0,  1, 0, 0, market=True), bar)

            #leaders -rezko poslednie, v sdelke - taim stop elsi ne v pluse

        #if get15minBarNum(bar[0]) in [7]:
        #    if perc < 0.1:
        #        self.engine.sendOrder(Order(bar[11], 1, 0, 0, 0,  1, 0, 0, market=True), bar)


        if perc < 0.3:
            #if v < 0.3:
            self.engine.sendOrder(Order(bar[11], 1, 0, 0, 0,  1, 0, 0, market=True), bar)





    def onStop(self):

        if self.pOptimization is True:
            print self.pOpt
            self.engine.generateTextReport(self.lotSizeInUSD, self.commissionPerPip)
            return


        self.engine.printTrades(self.lotSizeInUSD, self.commissionPerPip)
        self.engine.generateTextReport(self.lotSizeInUSD, self.commissionPerPip)
        self.engine.showEquity(self.lotSizeInUSD, self.commissionPerPip)
        self.engine.getProfitsByTimeOfDay(self.lotSizeInUSD, self.commissionPerPip,)

        self.engine.getFilterAnalyze(self.lotSizeInUSD,  self.commissionPerPip, 0, 50)

        #for p in self.engine.getClosedPositions():
        #    self.engine.showTrade(p, 'EUR/USD')


        #self.engine.getFilterAnalyze(self.lotSizeInUSD,  self.commissionPerPip, 0, 50)


        #self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 0, longOnly=True)
        #self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 0, longOnly=True, leaders=True, nOfL=40)
        #self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 0, longOnly=True, loosers=True, nOfL=40)

        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 0, shortOnly=True)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 0, shortOnly=True, leaders=True, nOfL=40)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 0, shortOnly=True, loosers=True, nOfL=40)


        #self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, longOnly=True)
        #self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, longOnly=True, leaders=True, nOfL=40)
        #self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, longOnly=True, loosers=True, nOfL=40)

        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, shortOnly=True)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, shortOnly=True, leaders=True, nOfL=40)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, shortOnly=True, loosers=True, nOfL=40)



        self.engine.getMonthlyReturns(self.lotSizeInUSD, self.commissionPerPip)
        self.engine.getProfitsByDayOfWeek(self.lotSizeInUSD, self.commissionPerPip)






