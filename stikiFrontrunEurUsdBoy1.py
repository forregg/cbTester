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
        self.name = 'eurusdsfr'
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
        #return self.getSantimentShort(2*60, 0.0002)
        return self.engine.getHistoryBars(self.engine.data[0].name, 6*60, 0)


    def onGetStatOnPositionClose(self, position, bar):
        return self.engine.getHistoryBars(self.engine.data[0].name, 5, 0)

    def onBar(self, bar):

        if bar[2] == bar[3] and bar[5] == 0:
            return


        positionTimeStop = 2*10
        positionTimeStop = timedelta(seconds=positionTimeStop)

        positionTimeStopShort = 2*10
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

        #if forexSessions.isSummerTimeInLondon(bar[0]) is True:
        #    return

        #if get15minBarNum(bar[0]) not in [51]:#12.00-12.15
        #    return

        if bar[0].minute not in [59]:#range(0,60,5)
            return

        if bar[0].second not in [50]:#range(0,60,5)
            return

        data = self.engine.getHistoryBars(self.engine.data[0].name, 58 * 6, 0)
        if data == []:
            return
        tradeL = False
        tradeS = False

        for b in data:
            if b[0].minute == 30 and b[0].second == 10:
                if b[4]-b[1] > 0.0001:
                    tradeL = True

                if b[4]-b[1] < -0.0001:
                    tradeS = True


        vola = [ 0.00114444,  0.00109167,  0.00112207,  0.00133776,  0.00151162,  0.00136486,
                0.00119028,  0.00111101,  0.00114379,  0.0014608,   0.00207106,  0.00235503,
                0.00221462,  0.0021053,   0.0019202,   0.00202878,  0.00271961,  0.00266604,
                0.00273897,  0.00234986,  0.00189092,  0.00172452,  0.00169345,  0.0014114 ]



        #if data[len(data)-1,4] - data[0, 1] > 0.002:
        #    if tradeL == True:
        #        self.engine.sendOrder(Order(bar[11], 1, 0, 0, 0,  1, 0, 0, market=True), bar)


        if data[len(data)-1,4] - data[0, 1] < -0.0005  * 5:
            if tradeS == True:
                self.engine.sendOrder(Order(bar[11], -1, 0, 0, 0,  1, 0, 0, market=True), bar)

        #if data[len(data)-1,4] - data[0, 1] < -1 * vola[bar[0].hour + 3] * 1.5:
        #    self.engine.sendOrder(Order(bar[11], -1, 0, 0, 0,  1, 0, 0, market=True), bar)





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

        #self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 0, longOnly=True)
        #self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 0, longOnly=True, leaders=True, nOfL=40)
        #self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 0, longOnly=True, loosers=True, nOfL=40)

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






