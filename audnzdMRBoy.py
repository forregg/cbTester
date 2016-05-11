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
class AudnzdMrBoy(Strategy):
#params

    def __init__(self, engine, params):
        self.name = 'audnzdmr'
        self.engine = engine
        self.lotSizeInUSD = 675000
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

    def calculateVola(self, barsForward, samples, bar):
        data = self.engine.getHistoryBars(self.engine.data[0].name, samples * 24 * 60, 0)
        if data == []:
            return

        volas = []

        for i in range(len(data)):
            cBar = data[len(data)-1 - i]
            if cBar[0].minute == bar[0].minute and cBar[0].hour == bar[0].hour:
                pcHigh = np.max(data[len(data)-1-i:len(data)-1-i+barsForward, 6])
                pcLow = np.min(data[len(data)-1-i:len(data)-1-i+barsForward, 3])
                vola = pcHigh - pcLow
                volas.append(vola)
            else:
                continue

        #print np.average(volas)
        return np.around(np.average(volas), 5)

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
        return self.engine.getHistoryBars(self.engine.data[0].name, 360, 0)


    def onGetStatOnPositionClose(self, position, bar):
        return self.engine.getHistoryBars(self.engine.data[0].name, 360, 0)



    def onBar(self, bar):

        if bar[0].year not in [2012,2013,2014]:
            return

        if bar[2] == bar[3] and bar[5] == 0:
            return

        #if bar[0].year not in [2015]:
        #    return


        """ct = forexSessions.getCT(bar[0])

        if ct.hour == 16 and ct.minute == 14:
            positions = self.engine.getPositions()
            if len(positions) > 0:
                for p in reversed(positions):
                    self.engine.closePosition(p, bar)
        """


        positionTimeStop = 360
        positionTimeStop = timedelta(minutes=positionTimeStop)

        positionTimeStopShort = 360
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


        if bar[0].minute not in [0,15,30,45]:#range(0,60,5)
            return

        if get15minBarNum(bar[0]) not in range(0,17):
            return

        #if forexSessions.isSummerTimeInNY(bar[0]) is False:
        #    pass
        #else:
        #    return


        #if get15minBarNum(bar[0]) not in range(55,97) and get15minBarNum(bar[0]) not in range(31,40):#[55,56,57,58,60,61,62,63]:
        #    return
        #if get15minBarNum(ct) not in range(55-5*4,64-5*4):
        #    return

        pcPeriod = 12 * 60
        data = self.engine.getHistoryBars(self.engine.data[0].name, pcPeriod, 0)
        if data == []:
            return

        pcHigh = np.max(data[:, 7])
        pcHighTime = np.argmax(data[:, 7])
        pcLow = np.min(data[:, 3])
        pcLowTime = np.argmin(data[:, 3])


        pcPeriod = 1 * 60
        data = self.engine.getHistoryBars(self.engine.data[0].name, pcPeriod, 0)
        if data == []:
            return

        pcHigh2 = np.max(data[:, 2])
        pcLow2 = np.min(data[:, 3])


        if (pcHigh - pcLow) == 0:
            return

        percentOfRange = (bar[4] - pcLow) / (pcHigh - pcLow)



        #if (pcHigh2-pcLow2)  < 0.002:
        #    return

        #if data[0, 4] - data[len(data)-1,4] < 0:
        #    self.engine.sendOrder(Order(bar[11], -1, pcHigh, 0, pcLow2, 1, 0, 0, market=False), bar)
        #if data[0, 4] - data[len(data)-1,4] > 0:
        #if self.getSantiment(12*60, 0.0005) > 0.04:
        #    self.engine.sendOrder(Order(bar[11], 1, pcLow, 0, pcHigh2,  1, 0, 0, market=False), bar)
        #if percentOfRange < 0.02:
        #self.engine.sendOrder(Order(bar[11], -1, pcHigh, 0, pcLow2, 1, 0, 0, market=False), bar)
        #self.engine.sendOrder(Order(bar[11], 1, pcLow, 0, pcHigh2,  1, 0, 0, market=False), bar)
        #if self.getSantimentShort(12*60, 0.0002) > -0.27:
        #        if self.getSantimentShort(60, 0.0002) > -0.37:
        #if self.getSantimentLong(12*60, 0.0003) > 0.1:
        #    self.engine.sendOrder(Order(bar[11], -1, pcHigh, 0, pcLow2, 1, 0, 0, market=False), bar)
            #self.engine.sendOrder(Order(bar[11], -1, 0, 0, pcLow2, 1, 0, 0, market=True), bar)
        #if self.getSantimentShort(12*60, 0.0003) < -0.1:
            #self.engine.sendOrder(Order(bar[11], 1, pcLow, 0, pcHigh2-0.0002, 1, 0, 0, market=False), bar)
        self.engine.sendOrder(Order(bar[11], 1, pcLow, 0, 0, 1, 0, 0, market=False), bar)
        self.engine.sendOrder(Order(bar[11], -1, pcHigh, 0, 0, 1, 0, 0, market=False), bar)
        #if percentOfRange < 0.07:
            #if self.getSantimentShort(12*60, 0.0002) < 0.27:
            #self.engine.sendOrder(Order(bar[11], 1, pcLow, 0, pcHigh2 - 0.0001,  1, 0, 0, market=True), bar)

    def onStop(self):

        if self.pOptimization is True:
            print self.pOpt
            self.engine.generateTextReport(self.lotSizeInUSD, self.commissionPerPip)
            return

        self.engine.printTrades(self.lotSizeInUSD, self.commissionPerPip)
        self.engine.generateTextReport(self.lotSizeInUSD, self.commissionPerPip)
        self.engine.showEquity(self.lotSizeInUSD, self.commissionPerPip)

        #for p in self.engine.getClosedPositions():
        #    self.engine.showTrade(p, 'AUD/NZD')

        self.engine.getProfitsByTimeOfDay(self.lotSizeInUSD, self.commissionPerPip,)
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






