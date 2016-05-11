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
class SF(Strategy):
#params

    def __init__(self, engine, params):
        self.name = 'audnzdmr'
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

    def getSantimentShort(self, barsNum, porog = 0):
        bars = self.engine.getHistoryBars(self.engine.data[0].name, barsNum, 0)
        if bars == []:
            return 0
        santimentShort = 0
        santiment = 0
        for bar in bars:
            if bar[4] - bar[1] < -1*porog:
                santimentShort += (bar[4] - bar[1])
            santiment += abs(bar[1] - bar[4])
        if santiment == 0:
            return 0
        return santimentShort/santiment

    def getSantimentLong(self, barsNum, porog = 0):
        bars = self.engine.getHistoryBars(self.engine.data[0].name, barsNum, 0)
        if bars == []:
            return 0
        santimentLong = 0
        santiment = 0
        for bar in bars:
            if bar[4] - bar[1] > porog:
                santimentLong += (bar[4] - bar[1])
            santiment += abs(bar[1] - bar[4])
        if santiment == 0:
            return 0
        return santimentLong/santiment

    def onGetStatOnPositionOpen(self, position, bar):
        #return self.getSantimentShort(2*60, 0.0002)
        return self.engine.getHistoryBars(self.engine.data[0].name, 58+15, 0)


    def onGetStatOnPositionClose(self, position, bar):
        return self.engine.getHistoryBars(self.engine.data[0].name, 15, 0)



    def onBar(self, bar):

        if bar[0].year not in [2012,2013,2014,2015]:
            return

        if bar[2] == bar[3] and bar[5] == 0:
            return


        positionTimeStop = 2
        positionTimeStop = timedelta(minutes=positionTimeStop)

        positionTimeStopShort = 2
        positionTimeStopShort = timedelta(minutes=positionTimeStopShort)

        positions = self.engine.getPositions()
        if len(positions) > 0:
            for p in reversed(positions):
                if p.order.orderType == 1:
                    if p.openTime + positionTimeStop <= bar[0]:
                        self.engine.closePosition(p, bar)
                else:
                    if p.openTime + positionTimeStopShort <= bar[0]:
                        self.engine.closePosition(p, bar)


        tralTP = False

        if tralTP == True:
            positions = self.engine.getPositions()
            if len(positions) > 0:
                pcPeriod = 1 * 60
                data = self.engine.getHistoryBars(self.engine.data[0].name, pcPeriod, 0)
                if data == []:
                    return

                pcHigh2 = np.max(data[:, 2])
                pcLow2 = np.min(data[:, 3])

                shift = 0.0001

                for p in reversed(positions):
                    if p.order.orderType == 1:
                        if p.order.target > pcHigh2 - shift and bar[9] < pcHigh2 - shift:
                            self.engine.changeTarget(p, pcHigh2 - shift, bar)
                    else:
                        if p.order.target < pcLow2 + shift and bar[4] > pcLow2 + shift:
                            self.engine.changeTarget(p, pcLow2 + shift, bar)

        orderTimeStop = 15
        orderTimeStop = timedelta(minutes=orderTimeStop)

        orders = self.engine.getOrders()
        if len(orders) > 0:
            for o in reversed(orders):
                if o.openTime + orderTimeStop <= bar[0]:
                        self.engine.closeOrder(o)


        if bar[0].minute not in [59]:#range(0,60,5)
            return

        #if get15minBarNum(bar[0]) not in range(0,17):
        #    return


        pcPeriod = 58
        data = self.engine.getHistoryBars(self.engine.data[0].name, pcPeriod, 0)
        if data == []:
            return

        pcHigh = np.max(data[:, 7])
        pcHighTime = np.argmax(data[:, 7])
        pcLow = np.min(data[:, 3])
        pcLowTime = np.argmin(data[:, 3])


        if data[0, 4] - data[len(data)-1,4] < -1 * 4 * 0.001:
            self.engine.sendOrder(Order(bar[11], 1, 0, 0, 0,  1, 0, 0, market=True), bar)

        if data[0, 4] - data[len(data)-1,4] > 4 * 0.001:
            self.engine.sendOrder(Order(bar[11], -1, 0, 0, 0,  1, 0, 0, market=True), bar) #bar[4] - 0.0001 * self.pOpt

            #if self.getSantimentShort(12*60, 0.0002) < 0.27:


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
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, longOnly=True)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, longOnly=True, leaders=True, nOfL=30)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, longOnly=True, loosers=True, nOfL=30)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 0, longOnly=True)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 0, shortOnly=True)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 0, longOnly=True, leaders=True, nOfL=80)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 0, shortOnly=True, leaders=True, nOfL=40)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 0, longOnly=True, loosers=True, nOfL=80)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 0, shortOnly=True, loosers=True, nOfL=40)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, longOnly=True)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, shortOnly=True)

        self.engine.getMonthlyReturns(self.lotSizeInUSD, self.commissionPerPip)
        self.engine.getProfitsByDayOfWeek(self.lotSizeInUSD, self.commissionPerPip)






