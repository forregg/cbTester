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


    def onGetStatOnPositionOpen(self, position, bar):
        return self.engine.getHistoryBars(self.engine.data[0].name, 180, 0)


    def onGetStatOnPositionClose(self, position, bar):
        return self.engine.getHistoryBars(self.engine.data[0].name, 360, 0)

    def onBar(self, bar):

        if bar[0].year not in [2012,2013,2014,2015,2016]:
            return


        positions = self.engine.getPositions()
        if len(positions) > 0:
            for p in reversed(positions):
                if get15minBarNum(bar[0]) in [14]:
                #if bar[0].hour == 4 and bar[0].minute == 29:
                    self.engine.closePosition(p, bar)


        #positionTimeStop = 60 * 180
        #positionTimeStop = timedelta(seconds=positionTimeStop)

        #positionTimeStopShort = 180 * 60
        #positionTimeStopShort = timedelta(seconds=positionTimeStopShort)

        #positions = self.engine.getPositions()
        #if len(positions) > 0:
        #    for p in reversed(positions):
        #        if p.order.orderType == 1:
        #            if p.openTime + positionTimeStop <= bar[0]:
        #                self.engine.closePosition(p, bar)
        #        else:
        #            if p.openTime + positionTimeStopShort <= bar[0]:
        #                self.engine.closePosition(p, bar)

        #if forexSessions.isSummerTimeInLondon(bar[0]) is True:
        #    return

        if get15minBarNum(bar[0]) in [6,7]:

            if bar[0].minute not in [14,29,44,59]:#range(0,60,5)
                return

            data = self.engine.getHistoryBars(self.engine.data[0].name, 180, 0)
            if data == []:
                return
            pcHigh = np.max(data[:, 7])
            pcLow = np.min(data[:, 3])

            #if pcHigh - pcLow < 0.002:
            #    return

            #tradeL = False
            #tradeS = False


            #for b in data:
            #    if b[0].minute == 00 and b[0].hour == 21:
            #        if b[4]-b[1] > 0.0001:
            #            tradeL = True

            #        if b[4]-b[1] < -0.0001:
            #            tradeS = True


            perc = (bar[4]- pcLow)/ (pcHigh - pcLow)

            if get15minBarNum(bar[0]) in [5,6,7,8]:
                if perc < 0.3:
                    self.engine.sendOrder(Order(bar[11], 1, 0, 0, 0,  1, 0, 0, market=True), bar)
            #if get15minBarNum(bar[0]) in [7]:
            #    if perc > 0.1 and perc < 0.2:
            #        self.engine.sendOrder(Order(bar[11], 1, 0, 0, 0,  1, 0, 0, market=True), bar)

            #if get15minBarNum(bar[0]) in [7]:
            #    if perc < 0.1:
            #        self.engine.sendOrder(Order(bar[11], 1, 0, 0, 0,  1, 0, 0, market=True), bar)


            #if perc > 0.7:
            #    self.engine.sendOrder(Order(bar[11], -1, 0, 0, 0,  1, 0, 0, market=True), bar)

        if get15minBarNum(bar[0]) in []:#6]:#12.00-12.15
            if bar[0].minute not in [14,29,44,59]:#range(0,60,5)
                return

            data = self.engine.getHistoryBars(self.engine.data[0].name, 180, 0)
            if data == []:
                return
            pcHigh = np.max(data[:, 7])
            pcLow = np.min(data[:, 3])

            perc = (bar[4]- pcLow)/ (pcHigh - pcLow)

            if perc < 0.1:
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

        #for p in self.engine.getClosedPositions():
        #    self.engine.showTrade(p, 'EUR/USD')


        #self.engine.getFilterAnalyze(self.lotSizeInUSD,  self.commissionPerPip, 0, 50)


        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 0, longOnly=True)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 0, longOnly=True, leaders=True, nOfL=40)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 0, longOnly=True, loosers=True, nOfL=40)

        #self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 0, shortOnly=True)
        #self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 0, shortOnly=True, leaders=True, nOfL=40)
        #self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 0, shortOnly=True, loosers=True, nOfL=40)


        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, longOnly=True)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, longOnly=True, leaders=True, nOfL=40)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, longOnly=True, loosers=True, nOfL=40)

        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, shortOnly=True)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, shortOnly=True, leaders=True, nOfL=40)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, shortOnly=True, loosers=True, nOfL=40)



        self.engine.getMonthlyReturns(self.lotSizeInUSD, self.commissionPerPip)
        self.engine.getProfitsByDayOfWeek(self.lotSizeInUSD, self.commissionPerPip)






