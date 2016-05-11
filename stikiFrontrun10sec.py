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
        self.name = 'eurusd1sfr'
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
        return self.engine.getHistoryBars(self.engine.data[0].name, 6*60, 0)


    def onGetStatOnPositionClose(self, position, bar):
        return self.engine.getHistoryBars(self.engine.data[0].name, 8, 0)



    def onBar(self, bar):

        if bar[2] == bar[3] and bar[5] == 0:
            return


        positionTimeStop = 3*10
        positionTimeStop = timedelta(seconds=positionTimeStop)

        positionTimeStopShort = 3*10
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


        if bar[0].minute not in [59]:#range(0,60,5)
            return

        if bar[0].second not in [40]:#range(0,60,5)
            return

        if bar[0].hour not in range(5,22): #spread filter
            return

        #if get15minBarNum(bar[0]) not in [63]:
        #    return


        data = self.engine.getHistoryBars(self.engine.data[0].name, 58 * 6, 0)
        if data == []:
            return

        pcData = self.engine.getHistoryBars(self.engine.data[0].name, 9 * 6 * 60, 0)
        if pcData == []:
            return
        pcH = np.max(pcData[0:len(pcData)-60*6,2])
        pcL = np.min(pcData[0:len(pcData)-60*6,3])


        vola = [ 0.00114444,  0.00109167,  0.00112207,  0.00133776,  0.00151162,  0.00136486,
                0.00119028,  0.00111101,  0.00114379,  0.0014608,   0.00207106,  0.00235503,
                0.00221462,  0.0021053,   0.0019202,   0.00202878,  0.00271961,  0.00266604,
                0.00273897,  0.00234986,  0.00189092,  0.00172452,  0.00169345,  0.0014114 ]

        volaGbp = [ 0.00102141,  0.00089121,  0.00080093,  0.00104387,  0.00107892,  0.00088324,
                    0.00076055,  0.00077504,  0.00088622,  0.00155208,  0.00220972,  0.00266535,
                    0.00234841,  0.00203566,  0.00199956,  0.00258768,  0.00251581,  0.00262837,
                    0.00247429,  0.00192904,  0.00156832,  0.00151384,  0.00123301,  0.00105093]

        volaAud = [ 0.00089734,  0.00089016,  0.00089872,  0.00142538,  0.0017111,   0.00125599,
                    0.0011057,  0.00105881,  0.00099444,  0.00132999,  0.00154522,  0.00150066,
                    0.00129673,  0.00117797,  0.0011198,   0.00159575,  0.0017191,   0.00172981,
                    0.00152408,  0.00118795,  0.00103932,  0.00105903,  0.00093654,  0.00084858]

        averageVola = np.average(volaAud)


        #if volaAud[bar[0].hour] < averageVola:
        #    return



        #if data[len(data)-1,4] - data[0, 4] > volaGbp[bar[0].hour] * 3:
        #if data[len(data)-1,4] - data[0, 4] > averageVola * 2:
        if bar[4] > pcH:
            if data[len(data)-1,4] - data[0, 4] > volaAud[bar[0].hour] * 1.5:
                self.engine.sendOrder(Order(bar[11], 1, 0, 0, 0,  1, 0, 0, market=True), bar)


        #if data[len(data)-1,4] - data[0, 4] < -1 * averageVola * 2:
        #if data[len(data)-1,4] - data[0, 4] < -1 * volaGbp[bar[0].hour] * 3:

        if bar[4] < pcL:
            if data[len(data)-1,4] - data[0, 4] < -1 * volaAud[bar[0].hour] * 1.5:
                self.engine.sendOrder(Order(bar[11], -1, 0, 0, 0,  1, 0, 0, market=True), bar)





    def onStop(self):

        if self.pOptimization is True:
            print self.pOpt
            self.engine.generateTextReport(self.lotSizeInUSD, self.commissionPerPip)
            return


        self.engine.printTrades(self.lotSizeInUSD, self.commissionPerPip)
        self.engine.generateTextReport(self.lotSizeInUSD, self.commissionPerPip)
        self.engine.showEquity(self.lotSizeInUSD, self.commissionPerPip)
        self.engine.getProfitsByTimeOfDay(self.lotSizeInUSD, self.commissionPerPip,)

        for p in self.engine.getClosedPositions():
            self.engine.showTrade(p, 'EUR/USD')


        #self.engine.getFilterAnalyze(self.lotSizeInUSD,  self.commissionPerPip, 0, 50)

        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 0, longOnly=True)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 0, longOnly=True, leaders=True, nOfL=40)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 0, longOnly=True, loosers=True, nOfL=40)

        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 0, shortOnly=True)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 0, shortOnly=True, leaders=True, nOfL=40)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 0, shortOnly=True, loosers=True, nOfL=40)


        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, longOnly=True)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, longOnly=True, leaders=True, nOfL=40)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, longOnly=True, loosers=True, nOfL=40)

        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, shortOnly=True)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, shortOnly=True, leaders=True, nOfL=40)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, shortOnly=True, loosers=True, nOfL=40)



        self.engine.getMonthlyReturns(self.lotSizeInUSD, self.commissionPerPip)
        self.engine.getProfitsByDayOfWeek(self.lotSizeInUSD, self.commissionPerPip)






