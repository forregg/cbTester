from scipy import stats
import calendar
from datetime import timedelta

from strategy import Strategy
from order import Order
from trade import *
from forexSessions import *


class TestStrat(Strategy):
    name = 'testStrat'

    def __init__(self, engine, params):

        self.engine = engine
        if self.engine.name == 'Tester':
            self.lotSizeInUSD = 1000000
            self.commissionPerPip = self.lotSizeInUSD / 1000000 * 25
            if params != None:
                if 'pOptimization' in params:
                    self.pOptimization = params['pOptimization']
                if 'pOpt' in params:
                    self.pOpt = params['pOpt']


    def onStart(self):
        print 'test strat started ))'
        """ """

    def onGetStatOnPositionOpen(self, position, bar):
        return 0

    def onGetStatOnPositionClose(self, position, bar):
        return 0

    def onBar(self, bar):
        print bar
        #if bar[4] - bar[1] > 0:
        #    o = Order(instrument=bar[11], orderType=1, price=0, stop=bar[4] - 0.0002, target=bar[4] + 0.0002, lot=0.01, timeStopTime=0, positionTimeStopTime=0, market=True)
        #    self.engine.sendOrder(o, bar);

        #if bar[4] - bar[1] < 0:
        #    o = Order(instrument=bar[11], orderType=-1, price=0, stop=bar[4] + 0.0002, target=bar[4] - 0.0002, lot=0.01, timeStopTime=0, positionTimeStopTime=0, market=True)
        #    self.engine.sendOrder(o, bar);


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

        orderTimeStop = 15
        orderTimeStop = timedelta(minutes=orderTimeStop)

        orders = self.engine.getOrders()
        if len(orders) > 0:
            for o in reversed(orders):
                if o.openTime + orderTimeStop <= bar[0]:
                        self.engine.closeOrder(o)


        if bar[0].minute not in [0,15,30,45]:#range(0,60,5)
            print 'not our minute'
            return


        if get15minBarNum(bar[0]) not in [55,56,57,58,60,61,62,63]:
            print 'not our 15 min bar'
            return
        #if get15minBarNum(ct) not in range(55-5*4,64-5*4):
        #    return

        pcPeriod = 8 * 60
        data = self.engine.getHistoryBars(self.engine.data[0].name, pcPeriod, 0)
        if data == []:
            print 'history get error'
            return

        pcHigh = np.max(data[:, 7])
        pcHighTime = np.argmax(data[:, 7])
        pcLow = np.min(data[:, 3])
        pcLowTime = np.argmin(data[:, 3])

        pcPeriod = 3 * 60
        data = self.engine.getHistoryBars(self.engine.data[0].name, pcPeriod, 0)
        if data == []:
            print 'history get error'
            return

        pcHigh2 = np.max(data[:, 7])
        pcLow2 = np.min(data[:, 3])

        if (pcHigh - pcLow) == 0:
            print 'history get error'
            return

        f = True

        if f == True:
            if (pcHigh2-pcLow2)  < 0.002:
                print 'f: (pcHigh2-pcLow2)  < 0.002'
                return

        if data[0, 4] - data[len(data)-1,4] < 0:
            self.engine.sendOrder(Order(bar[11], -1, pcHigh, 0, pcLow2, 0.01, 0, 0, market=False), bar)
        else:
            print 'f: if data[0, 4] - data[len(data)-1,4] < 0:'
        if data[0, 4] - data[len(data)-1,4] > 0:
            self.engine.sendOrder(Order(bar[11], 1, pcLow, 0, pcHigh2,  0.01, 0, 0, market=False), bar)
        else:
            print 'f: if data[0, 4] - data[len(data)-1,4] > 0:'

    def onStop(self):
        print 'test strat stopped ))'
        if self.engine.name == 'Tester':
            self.engine.generateTextReport(self.lotSizeInUSD, self.commissionPerPip)
            self.engine.showEquity(self.lotSizeInUSD, self.commissionPerPip)
