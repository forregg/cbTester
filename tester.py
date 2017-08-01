import numpy as np
from order import Order
from position import Position
import matplotlib.pyplot as plt
from pylab import *
from scipy import stats
from trade import *
import calendar

class Tester():
    def __init__(self, data, strategyClass, strategyParams = None, getStat = False):
        self.name = 'Tester'
        self.positions = []
        self.closedPositions = []
        self.orders = []

        self.data = data
        self.getStat = getStat
        self.strategy = strategyClass(self, strategyParams)
        self.setTesterSettings()
        self.start()

    def setTesterSettings(self, slippage = 0, randomizeSlippage = True, point = 0.00001):
        self.slippage = slippage
        self.randomizeSlippage = randomizeSlippage
        self.point = point

    def start(self):
        self.strategy.onStart()

        d = np.array([])

        for instrument in self.data:
            names = [instrument.name for i in range(len(instrument.data[:, 0]))]
            if not d.size:
                d = np.column_stack((instrument.data, np.array(names)))
                instrument.data = d
            else:
                a = np.column_stack((instrument.data, np.array(names)))
                instrument.data = a
                d = np.vstack((d,a))

        if len(self.data) > 1:
            d = d[d[:,0].argsort()]

        ###main bars loop#######################################
        for bar in d:
            #encreasing current bar counters
            for instrument in self.data:
                if instrument.name == bar[11]:
                    instrument.currentBar += 1

            self.checkOrdersTimeStops(bar)
            self.checkPositionsTimeStops(bar)

            self.checkStopStops(bar)
            self.checkTargetLimits(bar)

            positionsCount = len(self.getPositions())
            self.checkEntryLimits(bar)
            if positionsCount != len(self.getPositions()):
                self.checkStopStops(bar)
            self.strategy.onBar(bar)
        ###main bars loop#######################################

        self.strategy.onStop()


    def sendOrder(self, order, bar):
        if order.openTime == 0:
                order.openTime = bar[0]
        if order.market:
            self.orders.append(order)
            self.openPosition(order, bar, market = True)
        else:
            self.orders.append(order)

    def closeOrder(self, order):
        self.orders.remove(order)

    def getOrders(self):
        return self.orders

    def openPosition(self, order, bar, market = False):
        position = 0
        if order.instrument != "" and order.instrument != bar[11]:
            print "bar of other instrument!" #exception here
            raise NotImplementedError

        if market:
            if order.orderType == -1:
                order.price = bar[4]
            else:
                order.price = bar[9]
            position = Position(order, bar[0], self.slippage, self.randomizeSlippage, self.point, stat = [])
            if self.getStat:
                position.stat = []
                position.stat.append(self.strategy.onGetStatOnPositionOpen(position, bar))
        else:
            position = Position(order, bar[0], stat = [])
            if self.getStat:
                position.stat = []
                position.stat.append(self.strategy.onGetStatOnPositionOpen(position, bar))


        self.positions.append(position)
        self.orders.remove(position.order)
        self.strategy.onOrderExecution(position.order)

    def closePosition(self, position, bar = None, price = 0,  market = False): #### bar - obiazatel'nij parametr!!!

        if bar == None:
            raise NotImplementedError

        if position.order.instrument != "" and position.order.instrument != bar[11]:
            print "bar of other instrument!" #exception here
            raise NotImplementedError

        if not price:
            if position.order.orderType == 1:
                price = bar[4]
            else:
                price = bar[9]

        self.positions.remove(position)
        if market:
            position.close(price, bar[0], self.slippage, self.randomizeSlippage, self.point)
        else:
            position.close(price, bar[0])

        if self.getStat:
            if position.stat:
                position.stat.append(self.strategy.onGetStatOnPositionClose(position, bar))
            else:
                position.stat = self.strategy.onGetStatOnPositionClose(position, bar)

        self.closedPositions.append(position)

    def changeTarget(self, position, target, bar):
        if position.order.orderType == 1:
            if target <= bar[4]:
                self.closePosition(position, bar, market=True)
            else:
                self.positions[self.positions.index(position)].order.target = target
        else:
            if target >= bar[9]:
                self.closePosition(position, bar, market=True)
            else:
                self.positions[self.positions.index(position)].order.target = target

    def getPositions(self):
        return self.positions

    def getClosedPositions(self):
        return self.closedPositions

    def getOrders(self):
        return self.orders

    def checkEntryLimits(self, bar):
        for order in reversed(self.orders):
            if order.instrument != "" and order.instrument != bar[11]:
                continue
            if order.orderType == 1:
                if bar[8] <= order.price <= bar[7]:
                    self.openPosition(order, bar)
                    continue
            if order.orderType == -1:
                if bar[3] <= order.price <= bar[2]:
                    self.openPosition(order, bar)
                    continue

    def checkTargetLimits(self, bar):
        for position in reversed(self.positions):
            if position.order.instrument != "" and position.order.instrument != bar[11]:
                continue
            if position.order.orderType == 1:
                if bar[3] <= position.order.target <= bar[2]:
                    self.closePosition(position, bar, position.order.target)
                    continue
            if position.order.orderType == -1:
                if bar[8] <= position.order.target <= bar[7]:
                    self.closePosition(position, bar, position.order.target)
                    continue

    def checkStopStops(self, bar):
        for position in reversed(self.positions):
            if position.order.instrument != "" and position.order.instrument != bar[11]:
                continue
            if position.order.orderType == 1:
                if bar[3] <= position.order.stop <= bar[2]:
                    self.closePosition(position, bar, position.order.stop, market = True)
                    continue
            if position.order.orderType == -1:
                if bar[8] <= position.order.stop <= bar[7]:
                    self.closePosition(position, bar, position.order.stop, market = True)
                    continue

    def checkPositionsTimeStops(self, bar):
        for position in reversed(self.positions):
            if position.order.instrument != "" and position.order.instrument != bar[11]:
                continue
            #time stop
#            if position.timeStopTime <=  bar[0]:
#                if position.order.orderType == 1:
#                    self.closePosition(position, bar[4], bar, market = True)
#                    continue
#                if position.order.orderType == -1:
#                    self.closePosition(position, bar[8], bar, market = True)
#                    continue
            if position.timeStopTime == 0:
                if position.order.orderType == 1:
                    self.closePosition(position, bar,  bar[4],market = True)
                    continue
                if position.order.orderType == -1:
                    self.closePosition(position, bar, bar[9], market = True)
                    continue
            position.timeStopTime -= 1

    def checkOrdersTimeStops(self, bar):
        for order in reversed(self.orders):
            if order.instrument != "" and order.instrument != bar[11]:
                continue
            #timestops
#            if order.timeStopTime <= bar[0]:
#                self.closeOrder(order)
#                continue
            if order.timeStopTime == 0:
                self.closeOrder(order)
                continue
            order.timeStopTime -= 1

    def checkOrdersActions(self, bar):
        for order in reversed(self.orders):
            if order.instrument != "" and order.instrument != bar[11]:
                continue
            #timestops
            if order.timeStopTime <= bar[0]:
                self.closeOrder(order)
                continue
            #execution
            self.checkEntryLimits(bar)
    def checkPositionsActions(self, bar):
        for position in reversed(self.positions):
            if position.order.instrument != "" and position.order.instrument != bar[11]:
                continue
            #time stop
            if position.timeStopTime <=  bar[0]:
                if position.order.orderType == 1:
                    self.closePosition(position, bar, bar[4])
                    continue
                if position.order.orderType == -1:
                    self.closePosition(position, bar, bar[9])
                    continue

            #stops and targets (stops first)
            if position.order.orderType == 1:
                if bar[3] <= position.order.stop <= bar[2]:
                    self.closePosition(position, bar, position.order.stop)
                    continue
                if bar[3] <= position.order.target <= bar[2]:
                    self.closePosition(position, bar, position.order.target)
                    continue
            if position.order.orderType == -1:
                if bar[8] <= position.order.stop <= bar[7]:
                    self.closePosition(position, bar, position.order.stop)
                    continue
                if bar[8] <= position.order.target <= bar[7]:
                    self.closePosition(position, bar, position.order.target)
                    continue

    def getHistoryBars(self, instrumentName, bars, shift = 0):
        for instrument in self.data:
            if instrument.name == instrumentName:
                if bars + shift <= instrument.currentBar:
                    return instrument.data[instrument.currentBar - bars - shift : instrument.currentBar - shift, :] # !!! shoud be - instrument.currentBar - bars - shift + 1
                else:
                    return []

    def getHistoryBarsByTime(self, instrumentName, startTime, stopTime):
        for instrument in self.data:
            if instrument.name == instrumentName:
                i = np.searchsorted(instrument.data[:,0], startTime)
                j = np.searchsorted(instrument.data[:,0], stopTime)
                return instrument.data[i + 1 : j + 1, :]
            else:
                return np.array([])

    def showEquity(self, pLotSizeInUSD = 1000000,  commission = 0):
        profits = []
        commissions = []
        dates = []
        for position in self.closedPositions:
            p = (position.closePrice - position.order.price) * position.order.orderType * pLotSizeInUSD - commission
            profits.append(p)
            commissions.append(-commission)
            dates.append(position.openTime)

        equity = np.cumsum(profits)


        plt.plot(dates, equity)
        plt.plot(dates, np.cumsum(commissions))
        plt.show()

        plt.hist(profits,100)
        plt.show()

    def printTrades(self, lotSizeInUSD = 1000000,  commissionPerPip = 0):
        for position in self.closedPositions:
            p = (position.closePrice - position.order.price) * position.order.orderType * lotSizeInUSD - commissionPerPip
            if position.order.orderType == 1:
                print '%s long %s, %s, %.5f, %.5f, %.2f, %.2f dow:%d' %(position.order.instrument, position.openTime, position.closeTime, position.openPrice,position.closePrice,p,(position.closePrice - position.order.price) * position.order.orderType/0.0001, calendar.weekday(position.openTime.year, position.openTime.month, position.openTime.day))
            else:
                print '%s short %s, %s, %.5f, %.5f, %.2f, %.2f dow:%d' %(position.order.instrument,position.openTime, position.closeTime, position.openPrice,position.closePrice,p,(position.closePrice - position.order.price) * position.order.orderType/0.0001, calendar.weekday(position.openTime.year, position.openTime.month, position.openTime.day))

    def generateTextReport(self, lotSizeInUSD = 1000000,  commissionPerPip = 0):
        profits = []
        profitsLong = []
        profitsShort = []


        for position in self.closedPositions:
            p = (position.closePrice - position.order.price) * position.order.orderType * lotSizeInUSD - commissionPerPip
            profits.append(p)
            if position.order.orderType == 1:
                profitsLong.append(p)
            else:
                profitsShort.append(p)

            #profit = (position.closePrice - position.order.price) * position.order.orderType * lotSizeInUSD - commissionPerPip
            #profits.append(profit)
            #if showTrades:
            #    print '%.5f\t%.5f\t %.2f\t%s\t%s'\
            #      %(position.openPrice, position.closePrice, profit, position.openTime, position.closeTime)

        p = np.array(profits)
        pl = np.array(profitsLong)
        ps = np.array(profitsShort)
        if p.size > 0:
            print 'tr. %d, win. %.2f, pr. %.2f, pf %.2f, mo %.2f, av. pr. %.2f, av. loss, %.2f, ap / al, %.2f' %(p.size, p[p>0].size/float(p.size), np.sum(p), np.sum(p[p>0])/-np.sum(p[p<0]), np.sum(p)/p.size, np.mean(p[p>0]), np.mean(p[p<0]), np.mean(p[p>0])/np.mean(p[p<0]))
        if pl.size > 0:
            print 'lo %d, win. %.2f, pr. %.2f, pf %.2f, mo %.2f, av. pr. %.2f, av. loss, %.2f, ap / al, %.2f' %(pl.size, pl[pl>0].size/float(pl.size), np.sum(pl), np.sum(pl[pl>0])/-np.sum(pl[pl<0]), np.sum(pl)/pl.size, np.mean(pl[pl>0]), np.mean(pl[pl<0]), np.mean(pl[pl>0])/np.mean(pl[pl<0]))
        if ps.size > 0:
            print 'sh %d, win. %.2f, pr. %.2f, pf %.2f, mo %.2f, av. pr. %.2f, av. loss, %.2f, ap / al, %.2f' %(ps.size, ps[ps>0].size/float(ps.size), np.sum(ps), np.sum(ps[ps>0])/-np.sum(ps[ps<0]), np.sum(ps)/ps.size, np.mean(ps[ps>0]), np.mean(ps[ps<0]), np.mean(ps[ps>0])/np.mean(ps[ps<0]))


    def quotesToCandlestick(self, data):
        from matplotlib.dates import date2num
        #result = [data[:,0],data[:,1],data[:,4],data[:,2],data[:,3]]
        return np.column_stack((date2num(data[:,0]),data[:,1],data[:,4],data[:,2],data[:,3]))
        #return zip(date2num(data[:,0]),data[:,1],data[:,4],data[:,2],data[:,3])

    def showTrade(self, position, instrumentName):
        #beforeBars = 300
        #afterBars = 100

        #barsNum = beforeBars + afterBars + (position.closeTime - position.openTime).seconds * 60
        secondsBeforeTrade = 60 * 60
        secondsAfterTrade = 60
        from datetime import timedelta
        data = self.getHistoryBarsByTime(instrumentName, position.openTime - timedelta(seconds=secondsBeforeTrade), position.closeTime + timedelta(seconds=secondsAfterTrade))

        from matplotlib.finance import candlestick


        fig = figure()
        fig.subplots_adjust(bottom=0.2)
        ax = fig.add_subplot(111)
        data = self.quotesToCandlestick(data)

        from matplotlib.lines import Line2D
        from matplotlib.dates import date2num
        color = 'red'
        if position.order.orderType is 1:
            color='green'

        candlestick(ax, data, width=0.00006, colorup='g', colordown='r')

        enter = Line2D(
        xdata=(date2num(position.openTime), date2num(position.closeTime)), ydata=(position.openPrice, position.closePrice),
        color=color,
        linewidth=5,
        antialiased=True,
        )

        if position.order.target is not 0:
            tp = Line2D(
            xdata=(date2num(position.openTime), date2num(position.closeTime)), ydata=(position.order.target, position.order.target),
            color='g',
            linewidth=0.5,
            antialiased=True,
            )
            ax.add_line(tp)

        if position.order.stop is not 0:
            sl = Line2D(
            xdata=(date2num(position.openTime), date2num(position.closeTime)), ydata=(position.order.stop, position.order.stop),
            color='r',
            linewidth=0.5,
            antialiased=True,
            )
            ax.add_line(sl)


        ax.add_line(enter)
        ax.autoscale_view()

        show()

    def getFilterAnalyze(self, lotSizeInUSD,  commissionPerPip, numberInStat=0, pieces = 20):
            stat = []
            for p in self.getClosedPositions():
                stat.append([(p.closePrice - p.order.price) * p.order.orderType * lotSizeInUSD - commissionPerPip, p.stat[numberInStat]])
            stat = np.array(stat)

            stat = stat[np.argsort(stat[:,1])]
            x = range(0,len(stat),len(stat)/pieces)
            y = []
            for i in x:
                y.append(np.sum(stat[i:i+len(stat)/pieces,0]))

            width = len(stat)/pieces
            plt.bar(x,y, width)
            plt.xticks(x, stat[x,1])
            fig = plt.figure(1)
            fig.autofmt_xdate(rotation=90)
            plt.show()


            stat = stat[np.argsort(stat[:,0])]

            plt.subplot(211)
            plt.plot(stat[:,0])
            plt.subplot(212)
            plt.plot(stat[:,1])
            plt.show()
            plt.hist(stat[:,1])
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
        for p in self.getClosedPositions():
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

    def getLongs(self, positions):
        longs = []
        for position in positions:
            if position.order.orderType == 1:
                longs.append(position)
        return longs

    def getShorts(self, positions):
        shorts = []
        for position in positions:
            if position.order.orderType == -1:
                shorts.append(position)
        return shorts

    def getLoosers(self, positions, nOfL=10):
        positions = sorted(positions, key=lambda position: (position.closePrice - position.order.price) * position.order.orderType)
        assert len(positions) > nOfL, 'len(positions) < nOfL'
        return positions[0:nOfL]

    def getWinners(self, positions, nOfL=10):
        positions = sorted(positions, key=lambda position: (position.closePrice - position.order.price) * position.order.orderType, reverse=True)
        assert len(positions) > nOfL, 'len(positions) < nOfL'
        return positions[0:nOfL]

    def get3MP(self, positions, numberInStat, barsAfterEntry, nOS = 100, afterEntry = False, showAll = False):
        compare = [positions,self.getWinners(positions,nOS), self.getLoosers(positions,nOS)]

        plt.plot(self.getMP(compare[0], numberInStat, barsAfterEntry, afterEntry, showAll), color = 'blue')
        plt.plot(self.getMP(compare[1], numberInStat, barsAfterEntry, afterEntry, showAll), color = 'green')
        plt.plot(self.getMP(compare[2], numberInStat, barsAfterEntry, afterEntry, showAll), color = 'red')
        plt.show()



    def getMP(self, positions, numberInStat, barsAfterEntry, afterEntry = False, showAll = False, showGraph = False):
        resLevels = np.arange(0, 1000, 1)
        resMp = np.zeros(resLevels.size)

        for position in positions:
            data = np.array(position.stat[numberInStat])
            if afterEntry is False:
                min = np.around(np.min(data[:len(data)-1-barsAfterEntry, 3]), 4)
                max = np.around(np.max(data[:len(data)-1-barsAfterEntry, 2]), 4)
            else:
                min = np.around(np.min(data[len(data)-barsAfterEntry:len(data)-1, 3]), 4)
                max = np.around(np.max(data[len(data)-barsAfterEntry:len(data)-1, 2]), 4)

            if showAll is True:
                min = np.around(np.min(data[:, 3]), 4)
                max = np.around(np.max(data[:, 2]), 4)
            if min == max:
                return 0

            levels = np.arange(min, max, 0.0001)

            for level in levels:
                j = 500 + (level - position.openPrice) / 0.0001
                for bar in data:
                    if bar[2] > level > bar[3]:
                        resMp[j] = resMp[j] + 1
        resMp = np.sqrt(resMp)
        if showGraph is True:
            plt.plot(resMp)
            plt.show()
        return resMp

    def getPointAnalyze(self, lotSizeInUSD,  commissionPerPip, numberInStat=0, longOnly=False, shortOnly=False, leaders=False, loosers=False, nOfL=10):
            #need to save bars history in onPositionOpen or onOrderSend
            stat = []
            dvizg = []
            h = []
            l = []
            averageEntry = 0
            count = 0

            positions = self.getClosedPositions()

            if loosers:
                positions = sorted(positions, key=lambda position: (position.closePrice - position.order.price) * position.order.orderType)
                assert len(positions) > nOfL, 'len(positions) < nOfL'
                positions = positions[0:nOfL]
            if leaders:
                positions = sorted(positions, key=lambda position: (position.closePrice - position.order.price) * position.order.orderType, reverse=True)
                assert len(positions) > nOfL, 'len(positions) < nOfL'
                positions = positions[0:nOfL]

            for p in positions:
                if longOnly is True and p.order.orderType != 1:
                    continue
                if shortOnly is True and p.order.orderType != -1:
                    continue

                profit = (p.closePrice - p.order.price) * p.order.orderType * lotSizeInUSD - commissionPerPip
                averageEntry += p.order.price
                #stat.append([p.stat[numberInStat], profit])
                bars = np.array(p.stat[numberInStat])
                count +=1

                if dvizg == []:
                    dvizg = bars[:, 4]
                    h = bars[:, 2]
                    l = bars[:, 3]
                else:
                    dvizg += bars[:, 4]
                    h += bars[:, 2]
                    l += bars[:, 3]

            dvizg /= count
            h /= count
            l /= count
            averageEntry /= count

            plt.axhline(y=averageEntry)
            plt.plot(dvizg)
            plt.plot(h)
            plt.plot(l)
            title = 'lot:'+str(lotSizeInUSD)+' commis:'+str(commissionPerPip)+' longOnly:'+str(longOnly)+' shortOnly:'+str(shortOnly)+' leaders:'+str(leaders)+' loosers:'+str(loosers)+' nOfL:'+str(nOfL)
            plt.title(title)
            plt.show()

    def getProfitsByTimeOfDay(self, lotSizeInUsd, commissionPerPip, year = 0, showPf = True):
        stat = np.zeros(24 * 4)

        profits = np.zeros(24 * 4)
        loses = np.zeros(24 * 4)
        deals = np.zeros(24 * 4)

        for p in self.getClosedPositions():
            if year is not 0:
                if p.openTime.year != year:
                    continue
            profit = (p.closePrice - p.order.price) * p.order.orderType * lotSizeInUsd - commissionPerPip
            stat[get15minBarNum(p.order.openTime)] += profit
            if profit > 0:
                profits[get15minBarNum(p.order.openTime)] += profit
                deals[get15minBarNum(p.order.openTime)] += 1
            if profit < 0:
                loses[get15minBarNum(p.order.openTime)] += profit
                deals[get15minBarNum(p.order.openTime)] += 1
        import matplotlib.pyplot as plt
        #plt.plot(stat)
        #plt.grid(color = 'b')
        #plt.show()

        plt.figure(1)
        plt.subplot(211)
        plt.axhline(y=0)
        plt.plot(stat)
        plt.subplot(212)
        plt.axhline(y=0)
        plt.plot(deals)
        plt.show()

        if showPf == True:
            pr = profits / loses
            pr = pr * -1
            plt.plot(pr)
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

    def getProfitsByDayOfWeek(self, lotSizeInUsd, commissionPerPip, year = 0):
        stat = np.zeros(7)

        for p in self.getClosedPositions():
            if year is not 0:
                if p.openTime.year != year:
                    continue
            profit = (p.closePrice - p.order.price) * p.order.orderType * lotSizeInUsd - commissionPerPip
            import calendar
            dow = calendar.weekday(p.order.openTime.year, p.order.openTime.month, p.order.openTime.day)
            stat[dow] += profit
        import matplotlib.pyplot as plt
        plt.plot(stat)
        plt.grid(color = 'b')
        plt.show()
