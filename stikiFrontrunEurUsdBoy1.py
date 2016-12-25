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
from tester import Tester
from quotesFromCsv import loadData
from instrument import Instrument





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

    def getDailyRangeVola(self, barsNum, samples = 30):
        data = self.engine.getHistoryBars(self.engine.data[0].name, 6 * 60 * 24 * (samples + 2), 0)
        if data == []:
            return

        vola = []

        for i in range(samples):
            h = np.max(data[len(data)-1 - (i * 24 * 60 * 6) - barsNum : len(data)-1 - (i * 24 * 60 * 6),2])
            l = np.min(data[len(data)-1 - (i * 24 * 60 * 6) - barsNum : len(data)-1 - (i * 24 * 60 * 6),3])
            vola.append(h-l)

        return vola

    def getPercentileOfDailyRangeVola(self,barsNum, samples = 30):

        vola = self.getDailyRangeVola(barsNum, samples)

        if vola == None:
            return

        data = self.engine.getHistoryBars(self.engine.data[0].name, barsNum, 0)
        if data == []:
            return

        pcHigh = np.max(data[:, 2])
        pcLow = np.min(data[:, 3])

        lastRangeVola = pcHigh-pcLow

        return stats.percentileofscore(vola, lastRangeVola)


    def onGetStatOnPositionOpen(self, position, bar):
        data = self.engine.getHistoryBars(self.engine.data[0].name, 58 * 6, 0)
        if data == []:
            return
        for b in data:
            if b[0].minute == 30 and b[0].second == 10:
                return b[2]-b[3]

        return self.engine.getHistoryBars(self.engine.data[0].name, 6*70, 0)


    def onGetStatOnPositionClose(self, position, bar):
        return self.engine.getHistoryBars(self.engine.data[0].name, 6*75, 0)

    def onBar(self, bar):

        if bar[2] == bar[3] and bar[5] == 0:
            return


        positionTimeStop = 3 * 10
        positionTimeStop = timedelta(seconds=positionTimeStop)

        positionTimeStopShort = 3 * 10
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

        if get15minBarNum(bar[0]) not in range(50,60):#[50,51,52]:#12.00-12.15
            return

        if bar[0].minute not in [59]:#range(0,60,5)
            return

        if bar[0].second not in [40]:#range(0,60,5)
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


        pcHigh = np.max(data[:, 7])
        pcLow = np.min(data[:, 3])

        perc = (bar[4]- pcLow)/ (pcHigh - pcLow)

        v = self.getPercentileOfDailyRangeVola(58 * 6, 30)
        v2 = self.getPercentileOfDailyRangeVola(58 * 6, 10)


        data2 = self.engine.getHistoryBars(self.engine.data[0].name, 5 * 6, 0)
        if data2 == []:
            return

        pcHigh = np.max(data2[:, 7])
        pcLow = np.min(data2[:, 3])

        if pcHigh < bar[7] + 0.0002: pcHigh = bar[7] + 0.0002
        if pcLow > bar[3] - 0.0002: pcLow = bar[3] - 0.0002


        if data[len(data)-1,4] - data[0, 1] > 0.0001 and v2 == 100:

            if perc < 0.95 and perc > 0.6:
                #if tradeL == True:
                self.engine.sendOrder(Order(bar[11], 1, 0, 0, 0,  1, 0, 0, market=True), bar)


        if data[len(data)-1,4] - data[0, 1] < -0.0001 and v2 == 100:
            if perc > 0.1 and perc < 0.4:
                #if tradeS == True:
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

        self.engine.getFilterAnalyze(self.lotSizeInUSD,  self.commissionPerPip, 0, 50)

        for p in self.engine.getClosedPositions():
            self.engine.showTrade(p, 'EUR/USD')

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






#data = loadData('/home/mage/PycharmProjects/cbTester/data/eurusd_10sec_110516.csv')
from getHistory import getHistoryFromDB
data = getHistoryFromDB('eurusd_10sec')
opt = False

if opt == True:
    for opt in range(70, 100, 5):
        strategyParams = {'pOptimization': True, 'pOpt':opt}
        tester = Tester([Instrument('EUR/USD', data)], SF, strategyParams, getStat=True)
else:
    strategyParams = {'pOptimization': False}
    tester = Tester([Instrument('eur', data)], SF, strategyParams, getStat=True)
