from abc import ABCMeta, abstractmethod


class Engine():
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, data, strategyClass, strategyParams=None, getStat=False):
        """ """

    @abstractmethod
    def start(self):
        """ """

    @abstractmethod
    def sendOrder(self, order, bar):
        """ """

    @abstractmethod
    def closeOrder(self, order):
        """ """

    @abstractmethod
    def getOrders(self):
        """ """

    @abstractmethod
    def closePosition(self, position, bar=None, price=0, market=False):
        """ """

    @abstractmethod
    def changeTarget(self, position, target, bar):
        """ """

    @abstractmethod
    def getPositions(self):
        """ """

    @abstractmethod
    def getClosedPositions(self):
        """ """

    @abstractmethod
    def getOrders(self):
        """ """

    @abstractmethod
    def checkPositionsTimeStops(self, bar):
        """ """

    @abstractmethod
    def checkOrdersTimeStops(self, bar):
        """ """

    @abstractmethod
    def checkOrdersActions(self, bar):
        """ """

    @abstractmethod
    def getHistoryBars(self, instrumentName, bars, shift=0):
        """ """

    @abstractmethod
    def getHistoryBarsByTime(self, instrumentName, startTime, stopTime):
        """ """
