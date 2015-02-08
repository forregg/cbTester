class Position:

    def __init__(self, order, openTime, slippage = 0, randomizeSlippage = True, point = 0.00001, stat = []):

        self.order = order
        if openTime:
            self.openTime = openTime
        else:
            self.openTime = order.openTime

        self.timeStopTime = order.positionTimeStopTime
        if not order.positionTimeStopTime:
            self.timeStopTime = -1

        #if order.positionTimeStopTime:
        #    self.timeStopTime = openTime + timedelta(0, order.positionTimeStopTime * 60)
        #else:
        #    self.timeStopTime = openTime + timedelta(100000)

        self.openPrice = order.price

        if slippage:
            if randomizeSlippage:
                from random import randrange
                if self.order.orderType == 1:
                    self.openPrice = self.openPrice + randrange(0, (int(slippage / point))) * point
                elif self.order.orderType == -1:
                    self.openPrice = self.openPrice - randrange(0, (int(slippage / point))) * point
            else:
                if self.order.orderType == 1:
                    self.openPrice = self.openPrice + self.slippage
                elif self.order.orderType == -1:
                    self.openPrice = self.openPrice - self.slippage
        self.stat = stat

    def close(self, closePrice, closeTime, slippage = 0, randomizeSlippage = True, point = 0.00001):

        self.closeTime = closeTime
        self.closePrice = closePrice

        if slippage:
            if randomizeSlippage:
                from random import randrange
                if self.order.orderType == 1:
                    self.closePrice = self.closePrice - randrange(0, (int(slippage / point))) * point
                elif self.order.orderType == -1:
                    self.closePrice = self.closePrice + randrange(0, (int(slippage / point))) * point
            else:
                if self.order.orderType == 1:
                    self.closePrice = self.closePrice - slippage
                elif self.order.orderType == -1:
                    self.closePrice = self.closePrice + slippage


