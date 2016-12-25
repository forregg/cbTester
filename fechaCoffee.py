from quotesFromDS import *
from matplotlib import pyplot as plt
data = loadDataRts('/home/mage/PycharmProjects/cbTester/data/@KC#_1.csv')
tradeOpened = False
startPrice = 0
endPrice = 0
trades = []

for bar in data:
    if bar[0].month == 5 and bar[0].day >= 20:
        if tradeOpened == False:
            print 'open: ' + str(bar)
            tradeOpened = True
            startPrice = bar[4]
    if bar[0].month == 6 and bar[0].day >= 20:
        if tradeOpened == True:
            print 'close: ' + str(bar)
            tradeOpened = False
            endPrice = bar[4]
            print 'result for sell on close =: ' + str(startPrice - endPrice)
            trades.append(startPrice - endPrice)

print 'cummulativ returns: ' + str(np.cumsum(trades))

plt.plot(np.cumsum(trades))
plt.show()

