from dukascopyEngine import DukascopyEngine
from strategy import Strategy
from order import Order
import numpy as np



class firstMio(Strategy):

    name = 'firstMio'

    def __init__(self, engine):
        self.name = 'firstMio'
        self.engine = engine

    def onStart(self):
        self.name = 'firstMio'
        print 'firstMio started..'

        #positions = self.engine.getPositions()
        #for p in positions:
        #    self.engine.closePosition(p)

    def onGetStatOnPositionOpen(self, position, bar):
        return 0

    def onGetStatOnPositionClose(self, position, bar):
        return 0

    def onBar(self, bar):


        if bar[11] != 'EUR/USD':
            return

        print bar

        interval = 24 * 4
        fw = 12

        if bar[0].minute in [14,29,44,59]:
            positions = self.engine.getPositions()
            for p in positions:
                self.engine.closePosition(p)
            return

        if bar[0].minute not in [2,17,32,47]:
            return

        a = self.engine.getHistoryBars('EUR/USD', interval, 0)
        b = self.engine.getHistoryBars('GBP/USD', interval, 0)
        c = self.engine.getHistoryBars('AUD/USD', interval, 0)
        d = self.engine.getHistoryBars('USD/CAD', interval, 0)

        a = a[:,4]
        b = b[:,4]
        c = c[:,4]
        d = d[:,4]

        #print a

        an = (a - np.mean(a))/np.std(a)
        bn = (b - np.mean(b))/np.std(b)
        cn = (c - np.mean(c))/np.std(c)
        dn = (d - np.mean(d))/np.std(d)

        #print an


        r = np.matrix((an,bn,cn, dn))
        cov = np.cov(r)
        cov = cov.astype(np.float64)
        value,vector = np.linalg.eig(cov)
        coef = vector[np.argmin(value)]
        #print(coef)

        f = coef[0]*a + coef[1]*b + coef[2]*c + coef[3]*d

        m = np.mean(f)
        s = np.std(f)

        #import matplotlib.pyplot as plt
        #plt.plot(f)
        #plt.axhline(m)
        #plt.axhline(m-s)
        #plt.axhline(m+s)
        #plt.show()


        if f[len(f)-1] > m + 2*s:
            print 'opening short'
            if coef[0] > 0:
                self.engine.sendOrder(Order('EUR/USD', -1, 0, 0, 0,  np.round(coef[0],2), 0, 0, market=True), bar)
            else:
                self.engine.sendOrder(Order('EUR/USD', 1, 0, 0, 0,  -1*np.round(coef[0],2), 0, 0, market=True), bar)
            if coef[1] > 0:
                self.engine.sendOrder(Order('GBP/USD', -1, 0, 0, 0,  np.round(coef[1],2), 0, 0, market=True), bar)
            else:
                self.engine.sendOrder(Order('GBP/USD', 1, 0, 0, 0,  -1*np.round(coef[1],2), 0, 0, market=True), bar)
            if coef[2] > 0:
                self.engine.sendOrder(Order('AUD/USD', -1, 0, 0, 0,  np.round(coef[2],2), 0, 0, market=True), bar)
            else:
                self.engine.sendOrder(Order('AUD/USD', 1, 0, 0, 0,  -1*np.round(coef[2],2), 0, 0, market=True), bar)
            if coef[3] > 0:
                self.engine.sendOrder(Order('USD/CAD', -1, 0, 0, 0,  np.round(coef[3],2), 0, 0, market=True), bar)
            else:
                self.engine.sendOrder(Order('USD/CAD', 1, 0, 0, 0,  -1*np.round(coef[3],2), 0, 0, market=True), bar)



        if f[len(f)-1] < m - 2*s:
            print 'opening long'
            if coef[0] < 0:
                self.engine.sendOrder(Order('EUR/USD', -1, 0, 0, 0,  -1*np.round(coef[0],2), 0, 0, market=True), bar)
            else:
                self.engine.sendOrder(Order('EUR/USD', 1, 0, 0, 0,  np.round(coef[0],2), 0, 0, market=True), bar)
            if coef[1] < 0:
                self.engine.sendOrder(Order('GBP/USD', -1, 0, 0, 0,  -1*np.round(coef[1],2), 0, 0, market=True), bar)
            else:
                self.engine.sendOrder(Order('GBP/USD', 1, 0, 0, 0,  np.round(coef[1],2), 0, 0, market=True), bar)
            if coef[2] < 0:
                self.engine.sendOrder(Order('AUD/USD', -1, 0, 0, 0,  -1*np.round(coef[2],2), 0, 0, market=True), bar)
            else:
                self.engine.sendOrder(Order('AUD/USD', 1, 0, 0, 0,  np.round(coef[2],2), 0, 0, market=True), bar)
            if coef[3] < 0:
                self.engine.sendOrder(Order('USD/CAD', -1, 0, 0, 0,  -1*np.round(coef[3],2), 0, 0, market=True), bar)
            else:
                self.engine.sendOrder(Order('USD/CAD', 1, 0, 0, 0,  np.round(coef[3],2), 0, 0, market=True), bar)



    def onStop(self):
        print 'firstMio stopped..'



engine = DukascopyEngine()
engine.connect(['USD/CAD', 'EUR/USD', 'GBP/USD', 'AUD/USD'], '1 Min', firstMio)