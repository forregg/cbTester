from strategy import Strategy
from order import Order
from position import Position
from trade import *
from datetime import timedelta, datetime
import matplotlib.pyplot as plt
from forexSessions import *
from scipy import stats
import calendar
class Mr(Strategy):
#params

    def __init__(self, engine, params):
        self.engine = engine

        self.lotSizeInUSD = 1000000
        self.commissionPerPip = self.lotSizeInUSD / 1000000 * 25
        if params != None:
            if 'pOptimization' in params:
                self.pOptimization = params['pOptimization']
            if 'pOpt' in params:
                self.pOpt = params['pOpt']

        getInstrumentStat(engine)

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
        return self.engine.getHistoryBars(self.engine.data[0].name, 480+300, 0)
        return get15minBarNum(bar[0])#self.engine.getHistoryBars(self.engine.data[0].name, 65, 0)


    def onBar(self, bar):
        if bar[0].date() < datetime.date(year=2008, month=02, day=1):
            return
#        if bar[0].minute not in [14,29,44,59]:#11.45-12.45
#            return

        #if forexSessions.isSummerTimeInLondon(bar[0]) is True:
        #    return

        """if get15minBarNum(bar[0]) not in [50,51,52,53]:#range(47,52):#12.00-12.15
            return

        if len(self.engine.getPositions()) > 0:
            for p in self.engine.getPositions():
                if bar[0].hour*60+bar[0].minute-p.order.openTime.hour*60-p.order.openTime.minute > 30:
                    if (bar[4] - p.order.price) * p.order.orderType < 0:
                        self.engine.closePosition(p, bar)
        """

        if get15minBarNum(bar[0]) not in [50]:#range(47,52):#12.00-12.15
            return

        dow = calendar.weekday(bar[0].year, bar[0].month, bar[0].day)
        if dow == 0:
            return

        pcPeriod = 8 * 60
        data = self.engine.getHistoryBars(self.engine.data[0].name, pcPeriod, 0)
        if data == []:
            return

        pcHigh = np.max(data[:, 6])
        pcHighTime = np.argmax(data[:, 6])
        pcLow = np.min(data[:, 3])
        pcLowTime = np.argmin(data[:, 3])



        shift = 0.0001

        barsNum = 4 * 60#(bar[0].hour - londonOpenTime) * 60 + bar[0].minute
        #bars = self.engine.getHistoryBars(self.engine.data[0].name, barsNum, 0)
        #if bars == []:
        #    return
        target = self.getWSMATarget(data[barsNum:len(data)-1,:])
        #target = pcLow + (pcHigh - pcLow)/2

        if (pcHigh - pcLow) == 0:
            return

        percentOfRange = (bar[4] - pcLow) / (pcHigh - pcLow)

        f = False

        holdBars = 67

        if len(self.engine.getPositions()) == 0:
            if percentOfRange < 0.05:
                if f == True:
                    historyPC = pcPeroidSizeDecile(self.engine, 10, 60 * 8, bar)
                    if historyPC == []:
                        return
                    if stats.percentileofscore(historyPC, pcHigh - pcLow) < 40 or stats.percentileofscore(historyPC, pcHigh - pcLow) > 90:
                        return
                self.engine.sendOrder(Order(1, bar[4], 0, 0, 1, 0, holdBars, market=True), bar)#pcLow + (pcHigh-pcLow)/2
            if percentOfRange > 0.95:
                if f == True:
                    historyPC = pcPeroidSizeDecile(self.engine, 10, 60 * 8, bar)
                    if historyPC == []:
                        return
                    if stats.percentileofscore(historyPC, pcHigh - pcLow) < 40 or stats.percentileofscore(historyPC, pcHigh - pcLow) > 90:
                        return
                self.engine.sendOrder(Order(-1, bar[4], 0, 0, 1, 0, holdBars, market=True), bar)#pcLow + (pcHigh-pcLow)/2

        """if len(self.engine.getPositions()) == 1:
            if percentOfRange < 0.05:
                if f == True:
                    historyPC = pcPeroidSizeDecile(self.engine, 10, 60 * 8, bar)
                    if historyPC == []:
                        return
                    if stats.percentileofscore(historyPC, pcHigh - pcLow) < 40 or stats.percentileofscore(historyPC, pcHigh - pcLow) > 90:
                        return
                self.engine.sendOrder(Order(1, bar[4], 0, target, 1, 0, holdBars, market=True), bar)#pcLow + (pcHigh-pcLow)/2
            if percentOfRange > 0.95:
                if f == True:
                    historyPC = pcPeroidSizeDecile(self.engine, 10, 60 * 8, bar)
                    if historyPC == []:
                        return
                    if stats.percentileofscore(historyPC, pcHigh - pcLow) < 40 or stats.percentileofscore(historyPC, pcHigh - pcLow) > 90:
                        return
                self.engine.sendOrder(Order(-1, bar[4], 0, target, 1, 0, holdBars, market=True), bar)#pcLow + (pcHigh-pcLow)/2
        """

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
        self.engine.getMonthlyReturns(self.lotSizeInUSD, self.commissionPerPip)
        self.engine.getProfitsByDayOfWeek(self.lotSizeInUSD, self.commissionPerPip)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, longOnly=True)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, longOnly=True, leaders=True, nOfL=200)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, longOnly=True, loosers=True, nOfL=200)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, shortOnly=True)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, shortOnly=True, leaders=True, nOfL=200)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, shortOnly=True, loosers=True, nOfL=200)
        self.engine.getProfitsByTimeOfDay(self.lotSizeInUSD, self.commissionPerPip)
        self.engine.getFilterAnalyze(self.lotSizeInUSD, self.commissionPerPip)
        #self.engine.getFilterAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1)
        #self.engine.getFilterAnalyzeDecile(self.lotSizeInUSD, self.commissionPerPip)
        for p in self.engine.getClosedPositions():
            #if (p.closePrice - p.order.price) * p.order.orderType * self.lotSizeInUSD - self.commissionPerPip < 0:
            self.engine.showTrade(p, 'eurusd')
            print p.order.price
            print p.closePrice
            print p.order.openTime
