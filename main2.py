from datetime import date

from tester import Tester
from quotesFromCsv import loadData
from instrument import Instrument
from audusdMR import MR

#engine = DukascopyEngine(['EUR/USD'], '1 Min', Mr)

data = loadData('/home/mage/PycharmProjects/cbTester/data/eurusd_1m_120516.csv_trimmed.csv')
opt = False

if opt == True:
    for opt in range(5, 25, 1):
        strategyParams = {'pOptimization': True, 'pOpt':opt}
        tester = Tester([Instrument('EUR/USD', data)], MR, strategyParams, getStat=True)
else:
    strategyParams = {'pOptimization': False}
    tester = Tester([Instrument('EUR/USD', data)], MR, strategyParams, getStat=True)
exit()
