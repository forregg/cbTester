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
class Mr(Strategy):
#params

    def __init__(self, engine, params):

        self.name = 'mr'

        self.engine = engine

        self.lotSizeInUSD = 1000000
        self.commissionPerPip = self.lotSizeInUSD / 1000000 * 25
        self.pOptimization = False
        if params != None:
            if 'pOptimization' in params:
                self.pOptimization = params['pOptimization']
            if 'pOpt' in params:
                self.pOpt = params['pOpt']

        #getInstrumentStat(engine)

    def onStart(self):
        """not implemented yet"""

    def getWSMATarget(self, bars):
        WSMA = 0
        vol = 0
        for bar in bars:
            WSMA += getVolumeOfBar(bar) * bar[4]
            vol += getVolumeOfBar(bar)
        if vol == 0:
            return 0
        return WSMA/vol

    def onGetStatOnPositionOpen(self, position, bar):
        return
        return bar[0].minute

        pcPeriod = 2 * 60
        data = self.engine.getHistoryBars(self.engine.data[0].name, pcPeriod, 10)
        if data == []:
            return

        pcHigh = np.max(data[:, 6])
        pcHighTime = np.argmax(data[:, 6])
        pcLow = np.min(data[:, 3])
        pcLowTime = np.argmin(data[:, 3])
        if position.order.orderType == 1:
            return pcLowTime
        if position.order.orderType == -1:
            return pcHighTime

    def onGetStatOnPositionClose(self, position, bar):
        return self.engine.getHistoryBars(self.engine.data[0].name, 500, 0)
        return get15minBarNum(bar[0])#self.engine.getHistoryBars(self.engine.data[0].name, 65, 0)


    def onBar(self, bar):

        #if bar[0].year not in [2011,2012,2013,2014]:
        if bar[0].year not in [2015]:
            return

        if bar[0].minute not in [1,16,31,46]:
            return

        #if forexSessions.isSummerTimeInLondon(bar[0]) is False:
        #    return

        positionTimeStop = 270
        positionTimeStop = timedelta(minutes=positionTimeStop)

        positionTimeStop1 = 120
        positionTimeStop1 = timedelta(minutes=positionTimeStop1)

        positions = self.engine.getPositions()
        if len(positions) > 0:
            for p in reversed(positions):
                if p.order.orderType == 1:
                    if p.openTime + positionTimeStop <= bar[0]:
                        self.engine.closePosition(p, bar)
                if p.order.orderType == -1:
                    if p.openTime + positionTimeStop1 <= bar[0]:
                        self.engine.closePosition(p, bar)



        if get15minBarNum(bar[0]) not in [11,12]:#12.00-12.15
            return

        #dow = calendar.weekday(bar[0].year, bar[0].month, bar[0].day)
        #if dow == 0:
        #    return

        pcPeriod = 8 * 60
        data = self.engine.getHistoryBars(self.engine.data[0].name, pcPeriod, 0)
        if data == []:
            return

        pcHigh = np.max(data[:, 6])
        pcHighTime = np.argmax(data[:, 6])
        pcLow = np.min(data[:, 3])
        pcLowTime = np.argmin(data[:, 3])

        if (pcHigh - pcLow) == 0:
            return

        percentOfRange = (bar[4] - pcLow) / (pcHigh - pcLow)


        targetLong = pcLow + (pcHigh - pcLow)/2
        targetShort = pcHigh - (pcHigh - pcLow)/2

        f = False

        if len(self.engine.getPositions()) >= 0:
            if percentOfRange > 0.2:
                if f == True:
                    historyPC = pcPeroidSizeDecile(self.engine, 10, 60 * 8, bar)
                    if historyPC == []:
                        return
                    if stats.percentileofscore(historyPC, pcHigh - pcLow) < 60 or stats.percentileofscore(historyPC, pcHigh - pcLow) > 90:
                        return
                self.engine.sendOrder(Order(bar[11], 1, bar[4], 0, 0, 1, 0, 0, market=True), bar)#pcLow + (pcHigh-pcLow)/2
            if percentOfRange < 0.8:
                if f == True:
                    historyPC = pcPeroidSizeDecile(self.engine, 10, 60 * 8, bar)
                    if historyPC == []:
                        return
                    if stats.percentileofscore(historyPC, pcHigh - pcLow) < 60 or stats.percentileofscore(historyPC, pcHigh - pcLow) > 90:
                        return
                self.engine.sendOrder(Order(bar[11], -1, bar[4], 0, 0, 1, 0, 0, market=True), bar)#pcLow + (pcHigh-pcLow)/2

    def onStop(self):
        if self.pOptimization is True:
            print self.pOpt
            self.engine.generateTextReport(self.lotSizeInUSD, self.commissionPerPip)
            return


        self.engine.generateTextReport(self.lotSizeInUSD, self.commissionPerPip)
        if 1 == 0:
            holdBars = 300
            self.engine.get3MP(self.engine.getLongs(self.engine.getClosedPositions()), 1, holdBars, afterEntry = True)
            self.engine.get3MP(self.engine.getShorts(self.engine.getClosedPositions()), 1, holdBars, afterEntry = True)
            self.engine.get3MP(self.engine.getLongs(self.engine.getClosedPositions()), 1, holdBars)
            self.engine.get3MP(self.engine.getShorts(self.engine.getClosedPositions()), 1, holdBars)
            self.engine.get3MP(self.engine.getLongs(self.engine.getClosedPositions()), 1, holdBars, showAll=True)
            self.engine.get3MP(self.engine.getShorts(self.engine.getClosedPositions()), 1, holdBars, showAll=True)

        self.engine.printTrades(self.lotSizeInUSD, self.commissionPerPip)
        self.engine.showEquity(self.lotSizeInUSD, self.commissionPerPip)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, longOnly=True)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, shortOnly=True)
        self.engine.getProfitsByTimeOfDay(self.lotSizeInUSD, self.commissionPerPip)
        self.engine.getMonthlyReturns(self.lotSizeInUSD, self.commissionPerPip)
        self.engine.getProfitsByDayOfWeek(self.lotSizeInUSD, self.commissionPerPip)
        for p in self.engine.getClosedPositions():
            #if (p.closePrice - p.order.price) * p.order.orderType * self.lotSizeInUSD - self.commissionPerPip < 0:
            print p.order.price
            print p.closePrice
            print p.order.openTime
            self.engine.showTrade(p, 'EUR/USD')

        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, longOnly=True)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, longOnly=True, leaders=True, nOfL=200)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, longOnly=True, loosers=True, nOfL=200)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, shortOnly=True)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, shortOnly=True, leaders=True, nOfL=200)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, shortOnly=True, loosers=True, nOfL=200)

        self.engine.getFilterAnalyze(self.lotSizeInUSD, self.commissionPerPip)
        #self.engine.getFilterAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1)
        #self.engine.getFilterAnalyzeDecile(self.lotSizeInUSD, self.commissionPerPip)

