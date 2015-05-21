import zmq
from datetime import datetime
from order import *
import numpy as np

def p2p():
    print('connecting')
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://127.0.0.1:43002")

    for request in range(10000):
        print('sending request %s...' % request)
        socket.send('Hello--'+str(request))
        message = socket.recv()
        print "Received reply ", request, "[", message, "]"

    print 'finished'

def subscription():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect('tcp://127.0.0.1:43001')
    socket.setsockopt(zmq.SUBSCRIBE, 'GBP/USD')

    while True:
        msg = socket.recv()
        print msg


def sendOrder():
    print('connecting')
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://127.0.0.1:43002")

    print('sending order')
    order = ['sendOrder', 'mr', 'EUR/USD', 'SELL', '0.001', '0', '0', '0', '0', '0']
    command = '--'.join(order)
    socket.send(command)
    message = socket.recv()
    print "Received reply ", "[", message, "]"

    """
    String strategyName = parts[1];
    Instrument instrument = Instrument.fromString(parts[2]);
    IEngine.OrderCommand orderCommand = IEngine.OrderCommand.valueOf(parts[3]);
    Double ammount = Double.parseDouble(parts[4]);
    Double price = Double.parseDouble(parts[5]);
    Double slippage = Double.parseDouble(parts[6]);
    Double stopLossPrice = Double.parseDouble(parts[7]);
    Double takeProfitPrice = Double.parseDouble(parts[8]);
    Long goodTillTime = Long.parseLong(parts[9]);
    """

def closeOrder():
    print('connecting')
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://127.0.0.1:43002")

    print('sending order')
    order = ['sendOrder', 'mr', 'EUR/USD', 'BUY', '0.001', '0', '0', '0', '0', '0']
    command = '--'.join(order)
    socket.send(command)
    message = socket.recv()
    print "Received reply ", "[", message, "]"

def getOrders():
    print('connecting')
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://127.0.0.1:43002")

    print('getting orders')
    command = ['getOrders', 'mr', 'EUR/USD']
    command = '--'.join(command)
    socket.send(command)
    message = socket.recv()
    if message != '':
        print "Received reply ", "[", message, "]"
        orders = []
        orderStrings = message.split('-+-')
        for orderString in orderStrings:
            orderString = orderString.split('--')
            orders.append(Order(instrument=orderString[1], orderType=orderString[2], lot=orderString[3], price=orderString[4], stop=orderString[5],
                                target=orderString[6], timeStopTime=orderString[7], openTime=orderString[8]))
        for o in orders:
            print o

def getPositions():
    print('connecting')
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://127.0.0.1:43002")

    print('getting positions')
    command = ['getPositions', 'mr', 'EUR/USD']
    command = '--'.join(command)
    socket.send(command)
    message = socket.recv()
    if message != '':
        print "Received reply ", "[", message, "]"
        orders = []
        orderStrings = message.split('-+-')
        for orderString in orderStrings:
            orderString = orderString.split('--')
            orders.append(Order(instrument=orderString[1], orderType=orderString[2], lot=orderString[3], price=orderString[4], stop=orderString[5],
                                target=orderString[6], timeStopTime=orderString[7], openTime=orderString[8]))
        for o in orders:
            print o

def getHistoryBars():
    print('connecting')
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://127.0.0.1:43002")

    print('getting history')
    command = ['getHistory', 'EUR/USD', 'ONE_MIN', '100', '0', '0'] #command, intrument, period, barsBefore, shift, barsAfter
    command = '--'.join(command)
    socket.send(command)
    message = socket.recv()
    if message != '':
        print "Received reply ", "[", message, "]"
        bars = []
        barsStrings = message.split('-+-')
        for barStrings in barsStrings:
            bar = barStrings.split('--')
            bar[1] = datetime.fromtimestamp(float(bar[1]) / 1e3)
            bar = bar[1:]
            bars.append(bar)

        bars = np.array(bars)
        print bars
sendOrder()

#

#closeOrder()
#getOrders()
#getPositions()
#getHistoryBars()