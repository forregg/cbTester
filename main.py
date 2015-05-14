from datetime import date

from tester import Tester
from quotesFromCsv import loadData
from instrument import Instrument
from mr import Mr
from dukascopyEngine import DukascopyEngine



#strategyParams = {'pOptimization': False}
#engine = DukascopyEngine(['EUR/USD'], '1 Min', Mr, strategyParams, True)


startTest = date(2010, 1, 1)
stopTest = date(2012, 1, 1)

#data = quotesFromDS.loadData('D:\\GLOBALDATABASE\\COMMON\\RAWDATA\\Dukascopy\\1MIN\\FOREX\\AUDNZD_1.csv')
#data = data[:, [0, 1, 2, 3, 4, 6, 7, 8, 9]]

#data = loadData('c:\\eurusd_1.csv')
#data = loadData('c:\\nzdusd_1m.csv')

data = loadData('/home/mage/PycharmProjects/cbTester/data/eurusd_1m_20_03_2014.csv')

#for i in range(-5,6,1):
#    strategyParams = {'pOptimization': True, 'pShift': i}
#    tester = Tester([Instrument('audcad', data)], pcTests, strategyParams, True)

opt = False

#tester = Tester([Instrument('eurusd', data)], t, [], False)

if opt == True:
    for opt in range(4, 8, 1):
        strategyParams = {'pOptimization': True, 'pOpt':opt}
        tester = Tester([Instrument('EUR/USD', data)], Mr, strategyParams, True)
else:
    strategyParams = {'pOptimization': False}
    tester = Tester([Instrument('EUR/USD', data)], Mr, strategyParams, True)
#print data
#pcTests.run(data)

#data = [Instrument('eurusd', data)]


#!for opt in range(14, 74, 15):
#!    strategyParams = {'pExitMinute': opt, 'pOptimization': True}
#!    tester = Tester(data, t, strategyParams)

#strategyParams = {'pOptimization': False}
#tester = Tester(data, t, strategyParams)


#from multiprocessing import Process
#if __name__ == '__main__':
#    for exitMinute in range(55, 60, 1):
#        strategyParams = {'pOptimization': True,'pExitMinute': exitMinute}
        #tester = Tester(data, t, strategyParams)
        #th = threading.Thread(name='th'+str(exitMinute), target=Tester, args=(data, t, strategyParams))
        #th.start()

 #       p = Process(target=Tester, args=(data, t, strategyParams))
 #       p.start()
        #p.join()




#dates = data[:, 0]
#tate = dates[dates>startTest]
#print tate
#data = data[:, startTest > data[0, :] > startTest]

#data = [Instrument('nzdusd', data)]

#tester = Tester(data, movX)

