from datetime import date
import matplotlib.pyplot as plt
import numpy as np
from quotesFromCsv import loadData
from tester import Tester
from instrument import Instrument
from strategy import Strategy
from order import Order
import calendar
from forexSessions import *

from trade import *
from ma import ema

import quotesFromDS
from sklearn import preprocessing
from scipy.stats.stats import pearsonr

startTest = date(2010, 1, 1)
stopTest = date(2010, 5, 1)

usdchf = loadData('/home/mage/PycharmProjects/cbTester/data/usdchf_1m_200516.csv_trimmed.csv')
eurusd = loadData('/home/mage/PycharmProjects/cbTester/data/eurusd_1m_120516.csv_trimmed.csv')



class PairMeanRev(Strategy):
#params

    def __init__(self, engine, params):
        self.engine = engine
        self.lotSizeInUSD = 1000000
        self.commissionPerPip = self.lotSizeInUSD / 1000000 * 25
        self.result = []

        self.pOptimization = params['pOptimization']
        if self.pOptimization == True:
            self.pOpt = params['pOpt']
        self.queue = []
        self.queueClose = []

        self.cc = []
        self.lastBarInst1 = []
        self.lastBarInst2 = []

    def onBar(self, bar):

        if bar[0].date() < startTest or bar[0].date() > stopTest:
            return

        if bar[11] == self.engine.data[0].name:
            self.lastBarInst1 = bar

        if bar[11] == self.engine.data[1].name:
            self.lastBarInst2 = bar

        if self.lastBarInst1 == [] or self.lastBarInst2 == []:
            return

        if self.lastBarInst1[0] != self.lastBarInst2[0]:
            return

        if bar[0].minute != 59:
            return

        e = self.engine.getHistoryBars(self.engine.data[0].name, 60*24, 0)
        c = self.engine.getHistoryBars(self.engine.data[1].name, 60*24, 0)
        if e == []:
            return
        if c == []:
            return



        eOOS = self.engine.data[0].data[self.engine.data[0].currentBar : self.engine.data[0].currentBar + 24*60, 4]
        cOOS = self.engine.data[1].data[self.engine.data[0].currentBar : self.engine.data[0].currentBar + 24*60, 4]



        esrc = e[:,4]
        csrc = c[:,4]

        e = e[:,4]
        c = c[:,4]

        e = e-np.mean(e)
        c = c-np.mean(c)

        stde = np.std(e)
        stdc = np.std(c)

        if stde == 0 or stdc == 0:
            return

        e = e / np.std(e)
        c = c / np.std(c)

        c = c * -1

        #self.cc.append([pearsonr(e,c)[0], bar[0].hour])

        if pearsonr(e,c)[0] > 0.95:
            print str(pearsonr(e,c)[0]) + " " + str(pearsonr(eOOS,cOOS)[0])


        if pearsonr(e,c)[0] > 10.95:
            print pearsonr(e,c)[0]
            print pearsonr(eOOS,cOOS)[0]
            plt.figure(1)
            plt.subplot(511)
            plt.plot(e, label='eurusd')
            plt.plot(c, label='usdchf')
            plt.legend()
            plt.subplot(512)
            plt.plot(e-c)
            plt.subplot(513)
            plt.plot(esrc-np.mean(esrc)+csrc-np.mean(csrc))
            plt.subplot(514)
            plt.plot(eOOS-np.mean(eOOS)+cOOS-np.mean(cOOS))
            plt.subplot(515)
            plt.plot(eOOS-eOOS[0])
            plt.plot(cOOS-cOOS[0])
            plt.show()


        return

        #if get15minBarNum(bar[0]) not in range(22, 34):
        #        return

        for o in self.queue:
            if bar[11] == o[0]:
                self.engine.sendOrder(Order(o[0], o[1], 0, 0, 0, o[2], 0, 120, market=True), bar)
                self.queue.remove(o)

        for p in reversed(self.queueClose):
            if bar[11] == p.order.instrument:
                if p in self.engine.getPositions():
                    self.engine.closePosition(p, bar, market=True)
                self.queueClose.remove(p)


        e = self.engine.getHistoryBars(self.engine.data[0].name, 2 * 60, 0)
        c = self.engine.getHistoryBars(self.engine.data[1].name, 2 * 60, 0)
        if e == []:
            return
        if c == []:
            return

        pcHighE = np.max(e[:, 6])
        pcLowE = np.min(e[:, 3])
        pcHighC = np.max(c[:, 6])
        pcLowC = np.min(c[:, 3])

        if pcHighE == pcLowE or pcHighC == pcLowC:
            return

        pe = (e[len(e) - 1, 4] - pcLowE)/(pcHighE - pcLowE)
        pc = (c[len(c) - 1, 4] - pcLowC)/(pcHighC - pcLowC)

        r = pe-pc
        positions = self.engine.getPositions()

        if len(positions) > 0:
            profit = 0
            for p in reversed(positions):
                profit += (self.engine.getHistoryBars(p.order.instrument, 1, 0)[0, 4] - p.order.price) * p.order.orderType * self.lotSizeInUSD - self.commissionPerPip

            if profit > 5000:
               for p in reversed(positions):
                    if p not in self.queueClose:
                        self.queueClose.append(p)

        if len(positions) == 0:
            if pe > 0.85 and pc > 0.85:
                if bar[11] == "eurusd":
                    self.engine.sendOrder(Order("eurusd", 1, 0, 0, 0, 1, 0, 120, market=True), bar)
                    self.queue.append(["usdchf", 1, 1.4])
                if bar[11] == "usdchf":
                    self.engine.sendOrder(Order("usdchf", 1, 0, 0, 0, 1.4, 0, 120, market=True), bar)
                    self.queue.append(["eurusd", 1, 1])

        self.result.append(r)

    def onStop(self):
        import matplotlib.pyplot as plt
        """intraDayCc = []
        res = np.array(self.cc)
        for i in range(24):
            currentHour = res[res[:,1]==i]
            currentHour = currentHour[:,0]
            intraDayCc.append(np.average(currentHour))
        plt.plot(intraDayCc)
        plt.show()"""
        res = np.array(self.cc)
        plt.plot(res[:,0])
        plt.show()

        #autocorelation of kk
        #kk mean
        #kk stdev

        if self.pOptimization is False:
            self.engine.printTrades(self.lotSizeInUSD, self.commissionPerPip)
            self.engine.generateTextReport(self.lotSizeInUSD, self.commissionPerPip)
            self.engine.showEquity(self.lotSizeInUSD, self.commissionPerPip)
            self.engine.getProfitsByTimeOfDay(self.lotSizeInUSD, self.commissionPerPip,)
            self.engine.getFilterAnalyze(self.lotSizeInUSD, self.commissionPerPip)
            self.engine.getMonthlyReturns(self.lotSizeInUSD, self.commissionPerPip)
            self.engine.getProfitsByDayOfWeek(self.lotSizeInUSD, self.commissionPerPip)
            self.engine.getProfitsByTimeOfDay(self.lotSizeInUSD, self.commissionPerPip)
            self.engine.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1)
            import matplotlib.pyplot as plt
            plt.plot(self.result)
            plt.show()
        else:
            self.engine.generateTextReport(self.lotSizeInUSD, self.commissionPerPip)


    def onGetStatOnPositionOpen(self, position, bar):
        return

    def onGetStatOnPositionClose(self, position, bar):
        return


optimization = False

if optimization == True:
    for opt in range(30,190,30):
        tester = Tester([Instrument('eurusd', eurusd), Instrument('usdchf', usdchf)], PairMeanRev, {'pOptimization': True, 'pOpt':opt}, True)
else:
    tester = Tester([Instrument('eurusd', eurusd), Instrument('usdchf', usdchf)], PairMeanRev, {'pOptimization': False}, True)

