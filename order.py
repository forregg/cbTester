class Order:
    def __init__(self, orderType, price, stop, target, lot, timeStopTime = 0, positionTimeStopTime = 0, openTime = 0, active = True, market = False, instrument = ""):
        self.orderType, self.price, self.stop, self.target, self.lot, self.timeStopTime, self.positionTimeStopTime, self.openTime, self.active =\
        orderType, price, stop, target, lot, timeStopTime, positionTimeStopTime, openTime, active

        self.market = market

        self.instrument = instrument

        self.timeStopTime = timeStopTime
        if not timeStopTime:
            self.timeStopTime = -1
        #if openTime and timeStopTime:
        #    self.timeStopTime = openTime + timedelta(0, timeStopTime * 60)
        #else:
        #    self.timeStopTime = openTime + timedelta(1000)