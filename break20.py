from strategy import Strategy
from order import Order
from position import Position
from trade import *
from datetime import timedelta, datetime
import matplotlib.pyplot as plt
from forexSessions import *
from scipy import stats
import calendar
class Break20(Strategy):
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

        shift = (bar[0].hour - position.order.openTime.hour)*60 + bar[0].minute - position.order.openTime.minute
        orderOpenBar = self.engine.getHistoryBars(self.engine.data[0].name, 1, shift)
        return stats.percentileofscore(getVolumeHistory(self.engine, 20, orderOpenBar[0], 60*8), getVolumeHistory(self.engine, 1, orderOpenBar[0], 60*8))


    def onGetStatOnPositionClose(self, position, bar):
        return get15minBarNum(bar[0])#self.engine.getHistoryBars(self.engine.data[0].name, 65, 0)


    def onBar(self, bar):

        if bar[0].minute not in [14,29,44,59]:#11.45-12.45
            return

        #if forexSessions.isSummerTimeInLondon(bar[0]) is False:
        #    return

        #if get15minBarNum(bar[0]) in range(52,55):#12.00-12.15
            """
            positions = self.engine.getPositions()
            if len(positions) > 0:
                barsNum = 4 * 60#(bar[0].hour - londonOpenTime) * 60 + bar[0].minute
                bars = self.engine.getHistoryBars(self.engine.data[0].name, barsNum, 0)
                if bars == []:
                    return
                target = self.getWSMATarget(bars)
                for position in reversed(positions):
                    if position.order.orderType == 1:
                        if position.order.target > target and target > bar[8]:
                            self.engine.changeTarget(position, target, bar)
                        #if position.order.price > bar[8]:
                        #    self.engine.sendOrder(Order(1, 0, 0, target, 1, 0, 65-(bar[0]-position.openTime).seconds/60, market=True), bar)#pcLow + (pcHigh-pcLow)/2
                    if position.order.orderType == -1:
                        if position.order.target < target and target < bar[4]:
                            self.engine.changeTarget(position, target, bar)
                        #if position.order.price < bar[4]:
                        #    self.engine.sendOrder(Order(-1, 0, 0, target, 1, 0, 65-(bar[0]-position.openTime).seconds/60, market=True), bar)#pcLow + (pcHigh-pcLow)/2
        """


        if get15minBarNum(bar[0]) not in [49]:#range(47,52):#12.00-12.15
            return

        dow = calendar.weekday(bar[0].year, bar[0].month, bar[0].day)
        #if dow == 0:
        #    return

        pcPeriod = 8 * 60
        data = self.engine.getHistoryBars(self.engine.data[0].name, pcPeriod, 0)

        pcHigh = np.max(data[:, 6])
        pcHighTime = np.argmax(data[:, 6])
        pcLow = np.min(data[:, 3])
        pcLowTime = np.argmin(data[:, 3])

        historyPC = pcPeroidSizeDecile(self.engine, 10, 60 * 8, bar)
        if historyPC == []:
            return

        #filters
        #if stats.percentileofscore(getVolumeHistory(self.engine, 20, bar, 60*8), getVolumeHistory(self.engine, 1, bar, 60*8)) < 30:
        #    return
        #data = self.engine.getHistoryBars(self.engine.data[0].name, (get15minBarNum(bar[0]) - 7 * 4) * 15, 0)

        #if stats.percentileofscore(pcPeroidSizeDecile(self.engine, 10, 60 * 24, bar), pcHigh2 - pcLow2) > 90:
        #    return

        #if stats.percentileofscore(historyPC, pcHigh - pcLow) < 40 or stats.percentileofscore(historyPC, pcHigh - pcLow) > 90:
        #    return

        londonOpenTime = 7
        if forexSessions.isSummerTimeInLondon(bar[0]) is False:
            londonOpenTime = 8

        #result = stats.percentileofscore(distancesBetweenBars(self.engine, 10, bar, (get15minBarNum(bar[0]) - londonOpenTime * 4) * 15),distancesBetweenBars(self.engine, 1, bar, (get15minBarNum(bar[0]) - londonOpenTime * 4) * 15))
        #result = stats.percentileofscore(np.abs(distancesBetweenBars(self.engine, 10, bar, (get15minBarNum(bar[0]) - londonOpenTime * 4) * 15)),np.abs(distancesBetweenBars(self.engine, 1, bar, (get15minBarNum(bar[0]) - londonOpenTime * 4) * 15)))
        #if result > 90:
        #    return

        shift = 0.0001

        barsNum = 4 * 60#(bar[0].hour - londonOpenTime) * 60 + bar[0].minute
        bars = self.engine.getHistoryBars(self.engine.data[0].name, barsNum, 0)
        if bars == []:
            return
        target = self.getWSMATarget(bars)
        #target = 0

        """mp = getMarketProfile(self.engine, (get15minBarNum(bar[0]) - 7 * 4) * 15)#!!!
        if mp == []:
            return
        target = mp[np.argmax(mp[:,1]),0]
        """

        if pcLowTime < 472:
            self.engine.sendOrder(Order(1, pcLow - shift, 0, target, 1, 15, 65, market=False), bar)#pcLow + (pcHigh-pcLow)/2
        #print str(bar[0])+str(pcLow - shift)
        #self.engine.sendOrder(Order(1, pcLow - shift, 0, 0, 1, 15, 65, market=False), bar)#pcLow + (pcHigh-pcLow)/2
        #self.engine.sendOrder(Order(2, pcLow - shift * 20, 0, target - 0.001, 2, 15, 65, market=False), bar)#pcLow + (pcHigh-pcLow)/2
        if pcHighTime < 472:
            self.engine.sendOrder(Order(-1, pcHigh + shift, 0, target, 1, 15, 65, market=False), bar)#pcLow + (pcHigh-pcLow)/2
        #print str(bar[0])+str(pcHigh + shift)
        #self.engine.sendOrder(Order(-1, pcHigh + shift, 0, 0, 1, 15, 65, market=False), bar)#pcLow + (pcHigh-pcLow)/2
        #self.engine.sendOrder(Order(-1, pcHigh + shift * 20, 0, target + 0.001, 2, 15, 65, market=False), bar)#pcLow + (pcHigh-pcLow)/2


    def onStop(self):
        if self.pOptimization is True:
            print self.pOpt
            self.engine.generateTextReport(self.lotSizeInUSD, self.commissionPerPip)
            return

        self.engine.generateTextReport(self.lotSizeInUSD, self.commissionPerPip)
        self.engine.printTrades(self.lotSizeInUSD, self.commissionPerPip)
        self.engine.showEquity(self.lotSizeInUSD, self.commissionPerPip)
        self.engine.getMonthlyReturns(self.lotSizeInUSD, self.commissionPerPip)
        self.engine.getProfitsByDayOfWeek(self.lotSizeInUSD, self.commissionPerPip)
        #self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1)
        self.engine.getProfitsByTimeOfDay(self.lotSizeInUSD, self.commissionPerPip)
        self.engine.getFilterAnalyze(self.lotSizeInUSD, self.commissionPerPip)
        self.engine.getFilterAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1)
        #self.engine.getFilterAnalyzeDecile(self.lotSizeInUSD, self.commissionPerPip)
        for p in self.engine.getClosedPositions():
            #if (p.closePrice - p.order.price) * p.order.orderType * self.lotSizeInUSD - self.commissionPerPip < 0:
            self.engine.showTrade(p, 'eurusd')
            print p.order.price
            print p.closePrice
            print p.order.openTime
