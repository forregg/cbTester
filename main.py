from tester import Tester
from strategy import Strategy
from quotesFromCsv import loadData
from instrument import Instrument


class MyStrategy(Strategy):
    def onBar(self, bar):print bar[0]



class Bar:
    def __init__(self, t, ob, hb, lb, cb, oa, ha, la, ca, v):
        self.t, self.ob, self.hb, self.lb, self.cb, self.oa, self.ha, self.la, self.ca, self.v = t, ob, hb, lb, cb, oa, ha, la, ca, v

data = [Instrument('nzdusd', loadData('c:\\nzdusd_1m.csv')),
    Instrument('audusd', loadData('c:\\audusd_1m.csv'))]

tester = Tester(data, MyStrategy)
tester.start()
#tester = Tester(MyStrategy2)

ASAS..

asAS