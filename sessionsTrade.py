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
import pytz





class st(Strategy):
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
        return self.engine.getHistoryBars(self.engine.data[0].name, 6*60, 0)


    def onGetStatOnPositionClose(self, position, bar):
        return self.engine.getHistoryBars(self.engine.data[0].name, 4*60, 0)

    def onBar(self, bar):
        if bar[0].weekday() in [5,6]:
            return
        tzL = pytz.timezone('Europe/London')
        londonTime = tzL.fromutc(bar[0])
        tzNY = pytz.timezone('America/New_York')
        nyTime = tzNY.fromutc(bar[0])

        if londonTime.hour == 12 and londonTime.minute == 59:
            positions = self.engine.getPositions()
            if len(positions) > 0:
                for p in reversed(positions):
                    self.engine.closePosition(p, bar)
        if nyTime.hour == 13 and nyTime.minute == 29:
            positions = self.engine.getPositions()
            if len(positions) > 0:
                for p in reversed(positions):
                    self.engine.closePosition(p, bar)

        h = self.engine.getHistoryBars(self.engine.data[0].name, 60, 0)
        if h[len(h)-1][1] - h[0][1] < 0.0006:
            return
        #if londonTime.hour == 16 and londonTime.minute == 0:
        #    self.engine.sendOrder(Order(bar[11], 1, 0, 0, 0,  1, 0, 0, market=True), bar)
        if londonTime.hour == 9 and londonTime.minute == 0:
            self.engine.sendOrder(Order(bar[11], -1, 0, 0, 0,  1, 0, 0, market=True), bar)
        if londonTime.hour == 9 and londonTime.minute == 30:
            h = self.engine.getHistoryBars(self.engine.data[0].name, 60, 0)
            if bar[1] > h[0][1]:
                self.engine.sendOrder(Order(bar[11], -1, 0, 0, 0,  1, 0, 0, market=True), bar)
        #print londonTime
        #print nyTime


    def onStop(self):

        if self.pOptimization is True:
            print self.pOpt
            self.engine.generateTextReport(self.lotSizeInUSD, self.commissionPerPip)
            return


        self.engine.printTrades(self.lotSizeInUSD, self.commissionPerPip)
        self.engine.generateTextReport(self.lotSizeInUSD, self.commissionPerPip)
        self.engine.showEquity(self.lotSizeInUSD, self.commissionPerPip)
        #self.engine.getProfitsByTimeOfDay(self.lotSizeInUSD, self.commissionPerPip,)

        #self.engine.getFilterAnalyze(self.lotSizeInUSD,  self.commissionPerPip, 0, 50)

        #for p in self.engine.getClosedPositions():
        #    self.engine.showTrade(p, 'EUR/USD')

        #self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 0, longOnly=True)
        #self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 0, longOnly=True, leaders=True, nOfL=40)
        #self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 0, longOnly=True, loosers=True, nOfL=40)

        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 0, shortOnly=True)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 0, shortOnly=True, leaders=True, nOfL=40)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 0, shortOnly=True, loosers=True, nOfL=40)


        #self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, longOnly=True)
        #self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, longOnly=True, leaders=True, nOfL=40)
        #self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, longOnly=True, loosers=True, nOfL=40)

        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, shortOnly=True)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, shortOnly=True, leaders=True, nOfL=40)
        self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1, shortOnly=True, loosers=True, nOfL=40)



        self.engine.getMonthlyReturns(self.lotSizeInUSD, self.commissionPerPip)
        self.engine.getProfitsByDayOfWeek(self.lotSizeInUSD, self.commissionPerPip)


import postgresql as db
from getHistory import getHistoryFromDB

tableName = db.getTableName2('EUR/USD', 'ONE_MIN', "01/01/2012")
data = getHistoryFromDB(tableName)
opt = False

if opt == True:
    for opt in range(1, 10, 1):
        strategyParams = {'pOptimization': True, 'pOpt':opt}
        tester = Tester([Instrument('EUR/USD', data)], st, strategyParams, getStat=True)
else:
    strategyParams = {'pOptimization': False}
    tester = Tester([Instrument('EUR/USD', data)], st, strategyParams, getStat=True)
