from strategy import Strategy
from order import Order
from position import Position
from trade import *
from datetime import timedelta

class t(Strategy):
#params

    def __init__(self, engine, params):
        self.engine = engine

        self.pLotSizeInUSD = 1000000 #8.11 / 0.0001 #pip value in usd * pip size
        self.pCommissionPerPip = self.pLotSizeInUSD / 1000000 * 25#3.15
        self.pDigits = 5
        self.pExitMinute = 59
        self.pShift = 0.003
        self.pOptimization = False

        if params != None:
            if 'lotSizeInUSD' in params:
                self.pLotSizeInUSD = params['lotSizeInUSD']
            if 'commissionPerPip' in params:
                self.pCommissionPerPip = params['lotSizeInUSD']
            if 'digits' in params:
                self.pDigits = params['digits']
            if 'pExitMinute' in params:
                self.pExitMinute = params['pExitMinute']
            if 'pShift' in params:
                self.pShift = params['pShift']
            if 'pOptimization' in params:
                self.pOptimization = params['pOptimization']



    def onBar(self, bar):

        import pytz
        tzCST = pytz.timezone('America/Chicago')
        chicagoTime = tzCST.fromutc(bar[0])
        tzCET = pytz.timezone('Europe/Berlin')
        CETTime = tzCET.fromutc(bar[0])

        #print chicagoTime.hour
        #print chicagoTime

        if bar[0].year != 2013:
            return

        if bar[0].minute == 59 and bar[0].hour == 2:
            #print 'open' + str(bar[0])
            price = round(bar[4] - self.pShift * bar[4], self.pDigits);
            stop =  0#round(price - 0.01 * bar[4], self.pDigits);
            target = bar[4];
            self.engine.sendOrder(Order(1, price, stop, target, 1, 0, 0, bar[0]), bar)

            price = round(bar[4] + self.pShift * bar[4], self.pDigits);
            stop =  0#round(price + 0.01 * bar[4], self.pDigits);
            target = 0#round(price - 0.005, self.pDigits);
            self.engine.sendOrder(Order(-1, price, stop, target, 1, 0, 0, bar[0]), bar)

            price = round(bar[4] - 0.004 * bar[4], self.pDigits);
            self.engine.sendOrder(Order(1, price, stop, target, 1, 0, 0, bar[0]), bar)

            price = round(bar[4] + 0.004 * bar[4], self.pDigits);
            self.engine.sendOrder(Order(-1, price, stop, target, 1, 0, 0, bar[0]), bar)

            price = round(bar[4] - 0.005 * bar[4], self.pDigits);
            self.engine.sendOrder(Order(1, price, stop, target, 1, 0, 0, bar[0]), bar)

            price = round(bar[4] + 0.005 * bar[4], self.pDigits);
            self.engine.sendOrder(Order(-1, price, stop, target, 1, 0, 0, bar[0]), bar)


        if chicagoTime.minute == self.pExitMinute and chicagoTime.hour == 2:
            #print 'close' + str(bar[0])
            positions = self.engine.getPositions()
            orders = self.engine.getOrders()

            for position in reversed(positions):
                self.engine.closePosition(position, bar)

            for order in reversed(orders):
                self.engine.closeOrder(order)


    def onStop(self):
        print 'opt = ' + str(self.pExitMinute)
        self.engine.generateTextReport(self.pLotSizeInUSD, self.pCommissionPerPip)
        if self.pOptimization is False:
            self.engine.showEquity(self.pLotSizeInUSD, self.pCommissionPerPip)

