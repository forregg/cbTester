from strategy import Strategy
from order import Order
from position import Position
from trade import *
from datetime import timedelta, datetime
import matplotlib.pyplot as plt
from forexSessions import *
from scipy import stats

class Breakout(Strategy):
#params

    def __init__(self, engine, params):
        self.engine = engine

        self.lotSizeInUSD = 1000000
        #dlia audcad 0.98 / 1.039 * 1000000 #audcad / usdcad * lotSize
        self.commissionPerPip = self.lotSizeInUSD / 1000000 * 25
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

        self.getInstrumentStat(engine)

    def getInstrumentStat(self, engine):
        print 'asset growth: ' + str(np.round((engine.data[0].data[len(engine.data[0].data)-1,4]/engine.data[0].data[0,4] - 1) * 100,2))+'%'

    def maBid(self, bars):
        return np.sum(bars[:,4])/len(bars)

    def onGetStatOnPositionOpen(self, position, bar):
        b = self.getPCWidth(60 * 8, 14)
        r = 0
        if b !=  0:
            r = self.getPCWidth(60 * 2, 14)/b
        return r#[0]


    def getPCWidth(self, pcPeriod = 15 * 12, shift = 0):
        data = self.engine.getHistoryBars(self.engine.data[0].name, pcPeriod, shift)

        if data == []:
            return 0

        lowestLow = np.argmin(data[:, 3])
        pcLow = data[lowestLow, 3]
        highestHigh = np.argmax(data[:, 6])
        pcHigh = data[highestHigh, 6]

        return (pcHigh-pcLow)

    def getHistoryVolaByTime(self, startTime, minutes, samples):
        data = self.engine.getHistoryBars(self.engine.data[0].name, samples * 60 * 25, 0)

        if data == []:
            return []

        vola = []
        #s = 0
        for i in range(len(data) - minutes):
            if data[i, 0].minute == startTime[1] and data[i, 0].hour == startTime[0]:
                low = np.min(data[i:i+minutes, 3])
                high = np.max(data[i:i+minutes, 2])
                vola.append(high - low)
                #s += 1
        return vola



    def getPCExtremumsBarsNum(self, pcPeriod = 15 * 12, shift = 0):

        data = self.engine.getHistoryBars(self.engine.data[0].name, pcPeriod, shift)

        if data == []:
            return 0

        lowestLow = np.argmin(data[:, 3])
        highestHigh = np.argmax(data[:, 6])

        return [lowestLow,highestHigh]

    def onGetStatOnPositionClose(self, position, bar):
        return self.engine.getHistoryBars(self.engine.data[0].name, 180, 0)

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
        #if bar[0].year < 2011:
        #    return

        #if bar[0].year < 2009 or bar[0].year == 2013:
        #    return

        #if bar[0].minute not in [14,29,44,59]:
        #    return

        if forexSessions.isSummerTimeInLondon(bar[0]) is True:
            if self.get15minBarNum(bar[0]) not in [55]:
                 return

        if forexSessions.isSummerTimeInLondon(bar[0]) is False:
            if self.get15minBarNum(bar[0]) not in [58]:
                return

        positions = self.engine.getPositions()

        #vola = self.getHistoryVolaByTime([bar[0].hour, bar[0].minute], 15, 15)

        #if vola == []:
        #    return

        #vola = np.array(vola)
        #vola = stats.scoreatpercentile(vola, 80)

        pcPeriod = 60 * 8
        data = self.engine.getHistoryBars(self.engine.data[0].name, pcPeriod, 14)

        if data == []:
            return

        pcHigh = np.max(data[:, 2])
        pcHighTime = np.argmax(data[:, 2])

        pcLow = np.min(data[:, 3])
        pcLowTime = np.argmin(data[:, 3])

        data2 = self.engine.getHistoryBars(self.engine.data[0].name, 15, 0)
        h = np.max(data2[:, 2])
        l = np.min(data2[:, 3])

        b = self.getPCWidth(60 * 8, 14)
        r = 0
        if b !=  0:
            r = self.getPCWidth(60 * 2, 14)/b


        if r < 0.75:
            return

        """positions = self.engine.getPositions()
        for position in reversed(positions):
            if (bar[0] - position.openTime).seconds /60 >= 5:
                if position.order.orderType == 1:
                    if position.order.stop != position.openPrice:
                        if bar[8] > position.order.stop:
                            position.order.stop = position.openPrice
                else:
                    if position.order.stop != position.openPrice:
                        if bar[4] < position.order.stop:
                            position.order.stop = position.openPrice
        """
        #self.engine.sendOrder(Order(1, pcLow, 0, 0, 1, 15, 15), bar)
        #self.engine.sendOrder(Order(-1, pcHigh, 0, 0, 1, 15, 15), bar)

        if h > pcHigh + 0.001:
            #if pcHighTime < 60* 6:
            #if pcHighTime > (len(data) - 100):
            #if self.getPCWidth(60) > 0.01:
            self.engine.sendOrder(Order(1, 0, 0, 0, 1, 0, 15, market=True), bar)
            #self.engine.sendOrder(Order(1, bar[4] - 0.0005, 0, 0, 1, 15, 60), bar)
        if l < pcLow - 0.001:
            #if pcLowTime < 60* 6:
            #if pcHighTime > (len(data) - 100):
            #if self.getPCWidth(60) > 0.01:
            self.engine.sendOrder(Order(-1, 0, 0, 0, 1, 0, 15, market=True), bar)
            #self.engine.sendOrder(Order(1, bar[4] - 0.0005, 0, 0, 1, 15, 60), bar)



    def onStop(self):
        if self.pOptimization is True:
            print self.pOpt
            self.engine.generateTextReport(self.lotSizeInUSD, self.commissionPerPip)
            return

        self.engine.generateTextReport(self.lotSizeInUSD, self.commissionPerPip)
        self.engine.showEquity(self.lotSizeInUSD, self.commissionPerPip)
        self.getPointAnalyze(self.lotSizeInUSD, self.commissionPerPip, 1)
        self.getProfitsByTimeOfDay(self.lotSizeInUSD, self.commissionPerPip)
        self.getFilterAnalyze(self.lotSizeInUSD, self.commissionPerPip)
        for p in self.engine.getClosedPositions():
            self.engine.showTrade(p, 'eurusd')

    def getFilterAnalyze(self, lotSizeInUSD,  commissionPerPip, numberInStat=0, pieces = 50):
            stat = []
            for p in self.engine.getClosedPositions():
                stat.append([(p.closePrice - p.order.price) * p.order.orderType * lotSizeInUSD - commissionPerPip, p.stat[numberInStat]])
            stat = np.array(stat)
            ind = np.argsort(stat, axis=0)#.sort(1)
            print stat
            stat = stat[ind[:,0]]
            print stat
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


        r = stats.scoreatpercentile(stat, 80)

        #avg = np.average(stat)
        tradeBars = '['
        for i in range(24 * 4):
            #if stat[i] > 0:
            #    print str(i)+" "+str(stat[i])
            if stat[i] != 0 and stat[i] > r:
                tradeBars += str(i)+','
        tradeBars += ']'
        print tradeBars