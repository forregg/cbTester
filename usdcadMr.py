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
class UsdcadMr(Strategy):
#params

    def __init__(self, engine, params):
        self.name = 'usdcadmr'
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


    def onGetStatOnPositionOpen(self, position, bar):
        return self.engine.getHistoryBars(self.engine.data[0].name, 500, 0)


    def onGetStatOnPositionClose(self, position, bar):
        return self.engine.getHistoryBars(self.engine.data[0].name, 500, 0)



    def onBar(self, bar):

        if bar[0].year not in [2011,2012,2013,2014]:
            return
        #if bar[0].year not in [2015]:
        #    return


        ct = forexSessions.getCT(bar[0])

        if ct.hour == 16 and ct.minute == 14:
            positions = self.engine.getPositions()
            if len(positions) > 0:
                for p in reversed(positions):
                    self.engine.closePosition(p, bar)



        positionTimeStop = 800
        positionTimeStop = timedelta(minutes=positionTimeStop)

        positionTimeStopShort = 800
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
                pcPeriod = 8 * 60
                data = self.engine.getHistoryBars(self.engine.data[0].name, pcPeriod, 0)
                if data == []:
                    return

                pcHigh2 = np.max(data[:, 7])
                pcLow2 = np.min(data[:, 3])

                shift = self.pOpt * 0.0001

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


        #if forexSessions.isSummerTimeInNY(bar[0]) is False:
        #    pass
        #else:
        #    return


        if get15minBarNum(bar[0]) not in [58]:#[55,56,57,58,60,61,62,63]:
            return
        #if get15minBarNum(ct) not in range(55-5*4,64-5*4):
        #    return

        pcPeriod = 8 * 60
        data = self.engine.getHistoryBars(self.engine.data[0].name, pcPeriod, 0)
        if data == []:
            return

        pcHigh = np.max(data[:, 7])
        pcHighTime = np.argmax(data[:, 7])
        pcLow = np.min(data[:, 3])
        pcLowTime = np.argmin(data[:, 3])

        pcPeriod = 3 * 60
        data = self.engine.getHistoryBars(self.engine.data[0].name, pcPeriod, 0)
        if data == []:
            return

        pcHigh2 = np.max(data[:, 7])
        pcLow2 = np.min(data[:, 3])

        pcPeriod = 500
        data = self.engine.getHistoryBars(self.engine.data[0].name, pcPeriod, 0)
        if data == []:
            return

        pcHigh3 = np.max(data[:, 7])
        pcLow3 = np.min(data[:, 3])

        if (pcHigh - pcLow) == 0:
            return

        pcPeriod = 24 * 60 * 2
        data = self.engine.getHistoryBars(self.engine.data[0].name, pcPeriod, 0)
        if data == []:
            return

        pcHigh4 = np.max(data[:, 7])
        pcLow4 = np.min(data[:, 3])

        if (pcHigh - pcLow) == 0:
            return

        percentOfRange = (bar[4] - pcLow) / (pcHigh - pcLow)

        f = True

        if f == True:
            if (pcHigh2-pcLow2)  < 0.002:
                return


            #if (pcHigh4-pcLow4)  > 0.02:
            #    return
            #historyPC = pcPeroidSizeDecile(self.engine, 20, 60 * 8, bar)
            #if historyPC == []:
            #    return
            #if stats.percentileofscore(historyPC, pcHigh - pcLow) < self.pOpt * 10:
            #    return
            #if (pcHigh2-pcLow2) / (pcHigh3-pcLow3) < 0.9:
            #    return
        if data[0, 4] - data[len(data)-1,4] < 0:
            self.engine.sendOrder(Order(bar[11], -1, pcHigh, 0, pcLow2, 1, 0, 0, market=False), bar)
        if data[0, 4] - data[len(data)-1,4] > 0:
            self.engine.sendOrder(Order(bar[11], 1, pcLow, 0, pcHigh2,  1, 0, 0, market=False), bar)

    def onStop(self):

        if self.pOptimization is True:
            print self.pOpt
            self.engine.generateTextReport(self.lotSizeInUSD, self.commissionPerPip)
            return

        self.engine.printTrades(self.lotSizeInUSD, self.commissionPerPip)
        self.engine.generateTextReport(self.lotSizeInUSD, self.commissionPerPip)
        self.engine.showEquity(self.lotSizeInUSD, self.commissionPerPip)
        self.engine.getProfitsByTimeOfDay(self.lotSizeInUSD, self.commissionPerPip)
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






