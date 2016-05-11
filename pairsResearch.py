from quotesFromDS import loadDataRts
from matplotlib import pyplot as plt

res = loadDataRts('/home/mage/quotes/RI#_1.csv')
plt.plot(res[:, 4])
res2 = loadDataRts('/home/mage/quotes/Si#_1.csv')
plt.plot(res2[:, 4])
res3 = loadDataRts('/home/mage/quotes/BR#_1.csv')
plt.plot(res3[:, 4]*100)


plt.show()

print res