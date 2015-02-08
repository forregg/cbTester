from strategy import Strategy
from order import Order
from position import Position
from trade import *
from datetime import timedelta, datetime
import matplotlib.pyplot as plt
from forexSessions import *

class pcTests(Strategy):
#params

    def __init__(self, engine, params):
        self.engine = engine

        self.lotSizeInUSD = 137400
        #dlia audcad 0.98 / 1.039 * 1000000 #audcad / usdcad * lotSize
        self.commissionPerPip = 3.43
        #dlia audcad 23.67
        self.pDigits = 5
        self.pExitMinute = 59
        self.pShift = 0.003
        self.pOptimization = False
        self.pYear = 2013
        self.pPCPeriod = 15*4

        if params != None:
            if 'pOptimization' in params:
                self.pOptimization = params['pOptimization']
            if 'pOpt' in params:
                self.pOpt = params['pOpt']

    def maBid(self, bars):
        return np.sum(bars[:,4])/len(bars)

    def onGetStatOnPositionOpen(self, position, bar):
        #return self.getPCWidth(15 * 4 * 2)

        w = self.getPCExtremumsBarsNum(15 * 12)
        if position.order.orderType is 1:
            return w[0]
        else:
            return w[1]

        #return [(pcHigh2 - pcLow2)/(pcHigh - pcLow), self.engine.getHistoryBars(self.engine.data[0].name, 500, 0)]


    def getPCWidth(self, pcPeriod = 15 * 12):
        data = self.engine.getHistoryBars(self.engine.data[0].name, pcPeriod, 0)

        if data == []:
            return 0

        lowestLow = np.argmin(data[:, 3])
        pcLow = data[lowestLow, 3]
        highestHigh = np.argmax(data[:, 6])
        pcHigh = data[highestHigh, 6]

        return (pcHigh-pcLow)

    def getPCExtremumsBarsNum(self, pcPeriod = 15 * 12):

        data = self.engine.getHistoryBars(self.engine.data[0].name, pcPeriod, 0)

        if data == []:
            return 0

        lowestLow = np.argmin(data[:, 3])
        highestHigh = np.argmax(data[:, 6])

        return [lowestLow,highestHigh]


    def onGetStatOnPositionClose(self, position, bar):
        return
        #return (position.closeTime-position.openTime).seconds / 60
        #data = self.engine.getHistoryBars(self.engine.data[0].name, 2700, 0)
        #return data

    def get15MinVola(self, days = 7):
        data = self.engine.getHistoryBars(self.engine.data[0].name, (days + 1) * 24 * 60, 0)
        stat = np.zeros(24 * 4)

        i = 0
        if data == []:
            return []

        while data[i, 0].hour != 0 and data[i, 0].minute != 0:
            i += 1

        for i in range(i, i+(days * 24 * 60)+15, 15):
            v = np.max(data[i:i+15,2])-np.min(data[i:i+15,3])
            stat[data[i, 0].hour  * 4 + np.round(data[i, 0].minute/15, 0)] += v
        stat /= days
        return stat

    def get15minBarNum(self, time):
        return time.hour*4 + np.round(time.minute/15,0)

    def getMarketProfile(self, period):
        data = self.engine.getHistoryBars(self.engine.data[0].name, period, 0)

        if data == []:
            return 0

        low = np.min(data[:, 3])
        high = np.max(data[:, 2])

        res = []
        i = low
        while i <= high:
            num = 0
            for j in range(0,len(data)):
                if i >= data[j, 3] and i <= data[j, 2]:
                    num += 1
            res.append([i,num])
            i += 0.0001
        return np.array(res)

    def getFV(self, period):
        data = self.engine.getHistoryBars(self.engine.data[0].name, period, 0)

        if data == []:
            return 0

        fv = 0

        for i in range(len(data)):
            fv += data[i, 3] + (data[i, 2] - data[i, 3])
        return fv / len(data)


    def onBar(self, bar):

        #if self.pOptimization == True:
        #    if bar[0].year != self.pYear:
        #        return

        if bar[0].year < 2011:# or bar[0].year == 2013:# and bar[0].year != 2012:
            return

        tradeMinutes = [0, 15, 30, 45]
        trade15MinBars = range(12,29,1)

        #if self.get15minBarNum(bar[0]) not in trade15MinBars:
        #    return


        pcPeriodSmall = self.get15minBarNum(bar[0]) * 15

        if bar[0].minute not in tradeMinutes:
            return

        if forexSessions.isSummerTimeInLondon(bar[0]) is True:
            return

        data = self.engine.getHistoryBars(self.engine.data[0].name, pcPeriodSmall, 0)

        if data == []:
            return 0

        lowestLowSmall = np.argmin(data[:, 3])
        lowSmall = data[lowestLowSmall, 3]
        highestHighSmall = np.argmax(data[:, 6])
        highSmall = np.max(data[:, 6])
        """
        if self.get15minBarNum(bar[0]) == 28:
            positions = self.engine.getPositions()
            for position in reversed(positions):
                self.engine.closePosition(position, bar)
            return
        """

        """
        positions = self.engine.getPositions()
        for position in reversed(positions):
            if position.order.orderType == 1:
                if target < position.order.target:
                    self.engine.changeTarget(position, target, bar)
            else:
                if target > position.order.target:
                    self.engine.changeTarget(position, target, bar)
        """
        #if (highSmall-lowSmall) < 0.002:# or (highSmall-lowSmall) > 0.004:
        #    return

        #if lowestLowSmall < len(data) - 15 * 6:
            #self.engine.sendOrder(Order(1, lowSmall, lowSmall - stopSize, target, 1, 15, (27 + 4 - self.get15minBarNum(bar[0])) * 15), bar)
            #self.engine.sendOrder(Order(1, lowSmall, 0, 0, 1, 15, 4 * 15), bar)
        fv = self.getFV(pcPeriodSmall)
        self.engine.sendOrder(Order(1, lowSmall, 0, fv, 1, 15, 60 * 4), bar)
        #r = self.getMarketProfile(pcPeriodSmall)
        #plt.plot(r[:,1],r[:,0])
        #plt.plot(data[:,4])

        #plt.axhline(self.getFV(pcPeriodSmall))
        #plt.plot(range(0,len(data)), lowSmall)
        #plt.show()
        #if highestHighSmall < len(data) - 15 * 6:
            #self.engine.sendOrder(Order(-1, highSmall, highSmall + stopSize, target, 1, 15, (27 + 4 - self.get15minBarNum(bar[0])) * 15), bar)
        self.engine.sendOrder(Order(-1, highSmall, 0, fv, 1, 15, 60 * 4), bar)

    def onStop(self):


        self.engine.generateTextReport(self.lotSizeInUSD, self.commissionPerPip)

        #self.engine.generateTextReport(self.pLotSizeInUSD, self.pCommissionPerPip)

        #self.engine.showEquity(self.pLotSizeInUSD, self.pCommissionPerPip)
        #self.getMonthlyReturns(self.lotSizeInUSD, self.pCommissionPerPip)

        #self.getProfitsByTimeOfDay(self.lotSizeInUSD, self.pCommissionPerPip, 2012)
        if self.pOptimization is True:
            print self.pOpt
        else:
            self.engine.showEquity(self.lotSizeInUSD, self.commissionPerPip)
            #for p in self.engine.getClosedPositions():
            #    self.engine.showTrade(p, 'eurusd')
            self.getFilterAnalyze(self.lotSizeInUSD,  self.commissionPerPip, 0, 25)
            self.getProfitsByTimeOfDay(self.lotSizeInUSD, self.commissionPerPip)
        #self.getPointAnalyze(self.lotSizeInUSD,  self.commissionPerPip, 1)
        #self.getPointAnalyze(self.lotSizeInUSD,  self.commissionPerPip, 2)

        #self.getFilterAnalyze(self.lotSizeInUSD,  self.commissionPerPip, 0, 50)

        #else:
        #    print '---------------'

    def getFilterAnalyze(self, lotSizeInUSD,  commissionPerPip, numberInStat=0, pieces = 50):
            stat = []
            for p in self.engine.getClosedPositions():
                stat.append([p.stat[numberInStat], (p.closePrice - p.order.price) * p.order.orderType * lotSizeInUSD - commissionPerPip])
            stat = np.array(stat)
            ind = np.argsort(stat, axis=0)#.sort(1)
            stat = stat[ind[:,0]]
            plt.plot(stat[:,0])
            plt.show()
            plt.plot(stat[:,1])
            plt.show()

            k = []
            x = []
            for i in range(pieces):
                k.append(np.average(stat[i*np.round(len(stat)/pieces):(i+1)*np.round(len(stat)/pieces), 1]))
                x.append(stat[(i+1)*np.round(len(stat)/pieces - 1), 0])
            plt.grid(color = 'b')
            plt.plot(x,k)
            plt.show()


    def getMonthlyReturns(self, lotSizeInUSD,  commissionPerPip):
        prevMonth = 0
        profit = 0
        deals = 0
        monthlyReturns = []
        for p in self.engine.getClosedPositions():
            if prevMonth == 0:
                prevMonth = p.openTime.month
            profit += (p.closePrice - p.order.price) * p.order.orderType * lotSizeInUSD - commissionPerPip
            deals += 1
            if p.openTime.month != prevMonth:
                monthlyReturns.append([profit, deals])
                prevMonth = p.openTime.month
                profit = 0
                deals = 0
        result = np.array(monthlyReturns)
        import matplotlib.pyplot as plt
        plt.figure(1)
        plt.subplot(211)
        plt.axhline(y=0)
        plt.plot(result[:,0])
        plt.subplot(212)
        plt.axhline(y=0)
        plt.plot(result[:,1])
        plt.show()
        return result

    def getPointAnalyze(self, lotSizeInUSD,  commissionPerPip, numberInStat=0):
            #need to save bars history in onPositionOpen or onOrderSend
            stat = []
            dvizg = []
            h = []
            l = []
            averageEntry = 0
            for p in self.engine.getClosedPositions():
                #profit = (p.closePrice - p.order.price) * p.order.orderType * lotSizeInUSD - commissionPerPip
                averageEntry += p.order.price
                #stat.append([p.stat[numberInStat], profit])
                bars = np.array(p.stat[numberInStat])

                if dvizg == []:
                    dvizg = bars[:, 4]
                    h = bars[:, 2]
                    l = bars[:, 3]
                else:
                    dvizg += bars[:, 4]
                    h += bars[:, 2]
                    l += bars[:, 3]

            dvizg /= len(self.engine.getClosedPositions())
            h /= len(self.engine.getClosedPositions())
            l /= len(self.engine.getClosedPositions())
            averageEntry /= len(self.engine.getClosedPositions())

            plt.axhline(y=averageEntry)
            plt.plot(dvizg)
            plt.plot(h)
            plt.plot(l)
            plt.show()

    def getProfitsByTimeOfDay(self, lotSizeInUsd, commissionPerPip, year = 0):
        stat = np.zeros(24 * 4)

        for p in self.engine.getClosedPositions():
            if year is not 0:
                if p.openTime.year != year:
                    continue
            profit = (p.closePrice - p.order.price) * p.order.orderType * lotSizeInUsd - commissionPerPip
            stat[self.get15minBarNum(p.openTime)] += profit
        import matplotlib.pyplot as plt
        plt.plot(stat)
        plt.grid(color = 'b')
        plt.show()
        for i in range(24 * 4):
            #if stat[i] > 0:
            #    print str(i)+" "+str(stat[i])
            print str(stat[i])
