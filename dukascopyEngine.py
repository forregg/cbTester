import zmq
import numpy as np
from datetime import date, time, datetime
from order import *
from position import *
from strategy import Strategy


class DukascopyEngine():
    def __init__(self, instruments, period, strategyClass, strategyParams=None, getStat=False):
        self.name = 'Dukascopy'
        self.instruments = instruments
        self.period = period
        self.getStat = getStat
        self.strategy = strategyClass(self, strategyParams)
        self.strategyClass = strategyClass

        self.slippage = 0

        self.start()

    def __init__(self):
    #    """for use getHistory without runing strategy"""
        self.strategy = Strategy(self)


    def start(self):
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        socket.connect('tcp://127.0.0.1:43001')

        for instrument in self.instruments:
            socket.setsockopt(zmq.SUBSCRIBE, instrument)

        self.strategy.onStart()

        ###main bars loop#######################################
        while True:
            filter = socket.recv()
            bar = socket.recv()
            bar = bar.split(' ')

            if self.period != (bar[0] + " " + bar[1]):
                continue

            bar[2] = datetime.utcfromtimestamp(float(bar[2]) / 1e3)
            bar = np.array(bar)
            bar = bar[2:]
            bar[1:11] = bar[1:11].astype(np.float32, copy=False)
            bar[1:11] = np.around(bar[1:11].astype(np.double),5)
            self.strategy.onBar(bar)
        ###main bars loop#######################################

        self.strategy.onStop()

    def sendOrder(self, order, bar=None):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://127.0.0.1:43002")

        type = ""
        if order.market == True:
            if order.orderType == 1:
                type = "BUY"
            else:
                type = "SELL"
        else:
            if order.orderType == 1:
                type = "BUYLIMIT"
            else:
                type = "SELLLIMIT"

        order = ['sendOrder', self.strategyClass.name, order.instrument, type, str(order.lot), str(order.price),
                 str(self.slippage), str(order.stop), str(order.target), str(order.timeStopTime)]
        command = '--'.join(order)
        socket.send(command)
        message = socket.recv()
        return message

    def closeOrder(self, order, bar=None):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://127.0.0.1:43002")

        type = ""
        if order.market == True:
            if order.orderType == 1:
                type = "BUY"
            else:
                type = "SELL"
        else:
            if order.orderType == 1:
                type = "BUYLIMIT"
            else:
                type = "SELLLIMIT"

        order = ['closeOrder', self.strategy.name, order.instrument, type, str(order.lot), str(order.price),
                 str(self.slippage), str(order.stop), str(order.target), str(order.timeStopTime)]
        command = '--'.join(order)
        socket.send(command)
        message = socket.recv()
        return message

    def closePosition(self, position, bar=None):
        self.closeOrder(position.order, bar)

    def getOrders(self):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://127.0.0.1:43002")
        orders = []
        for instrument in self.instruments:
            command = ['getOrders', self.strategy.name, instrument]
            command = '--'.join(command)
            socket.send(command)
            message = socket.recv()
            if message != '':
                orderStrings = message.split('-+-')
                for orderString in orderStrings:
                    orderString = orderString.split('--')
                    market = True
                    orderType = 1
                    if orderString[2] == "SELL":
                        orderType = -1
                    if orderString[2] == "BUYLIMIT":
                        market = False
                    if orderString[2] == "SELLLIMIT":
                        orderType = -1
                        market = False
                    orders.append(
                        Order(instrument=orderString[1], orderType=orderType, market=market, lot=orderString[3],
                              price=orderString[4], stop=orderString[5],
                              target=orderString[6], timeStopTime=orderString[7], openTime=orderString[8]))
        return orders

    def getPositions(self):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://127.0.0.1:43002")

        positions = []
        for instrument in self.instruments:
            command = ['getPositions', self.strategy.name, instrument]
            command = '--'.join(command)
            socket.send(command)
            message = socket.recv()
            if message != '':
                positionStrings = message.split('-+-')
                for positionString in positionStrings:
                    positionString = positionString.split('--')
                    market = True
                    orderType = 1
                    if positionString[2] == "SELL":
                        orderType = -1
                    if positionString[2] == "BUYLIMIT":
                        market = False
                    if positionString[2] == "SELLLIMIT":
                        orderType = -1
                        market = False

                    timeStopTime = datetime.utcfromtimestamp(float(positionString[7]) / 1e3)
                    orderOpenTime = datetime.utcfromtimestamp(float(positionString[8]) / 1e3)
                    positionOpenTime = datetime.utcfromtimestamp(float(positionString[9]) / 1e3)

                    positions.append(Position(
                        Order(instrument=positionString[1], orderType=orderType, market=market, lot=positionString[3],
                              price=positionString[4], stop=positionString[5],
                              target=positionString[6], timeStopTime=timeStopTime, openTime=orderOpenTime),
                        openTime=positionOpenTime))
            return positions

    def getHistoryBars(self, instrument, barsBefore, shift, barsAfter=0, period='ONE_MIN', trimInstrument = False, filterWeekends = True):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://127.0.0.1:43002")
        command = ['getHistory', self.strategy.name, instrument, period, str(barsBefore), str(shift),
                   str(barsAfter), str(filterWeekends)]  # command, strategyName, intrument, period, barsBefore, shift, barsAfter
        command = '--'.join(command)
        socket.send(command)
        message = socket.recv()

        bars = []


        if message != '':
            barsStrings = message.split('-+-')
            for barStrings in barsStrings:
                bar = barStrings.split('--')

                bar[1] = datetime.utcfromtimestamp(float(bar[1]) / 1e3)
                bar = bar[1:]
                bar = np.array(bar)
                bar[1:11] = bar[1:11].astype(np.float32, copy=False)
                bar[1:11] = np.around(bar[1:11].astype(np.double),5)
                if trimInstrument == True:
                    bar = bar[:11]
                bars.append(bar)
            bars = np.array(bars)

        return bars