#from getHistory import getHistoryFromDB
#data = getHistoryFromDB('USD_CAD__ONE_MIN__5000000', updateQuotesFromSource=True)
#data = getHistoryFromDB('GBP_USD__ONE_MIN__5000000', updateQuotesFromSource=True)
#data = getHistoryFromDB('EUR_USD__ONE_MIN__5000000', updateQuotesFromSource=True)
#data = getHistoryFromDB('AUD_USD__ONE_MIN__5000000', updateQuotesFromSource=True)

from matplotlib import pyplot as plt
from getHistory import getHistoryFromDB
import numpy as np
import scipy as sp


#eurusd = getHistoryFromDB('EUR_USD__ONE_MIN')
#data = eurusd[:,4]
#data.dump('data/eurusdBTR.npy')


#plt.plot(eurusd[:,4])
#plt.plot(audusd[:,4])
#plt.plot(usdcad[:,4])
#plt.plot(gbpcad[:,4])


"""
data = np.load('data/USD_CAD__ONE_MIN_trimmed.csv.npy')
data = data[:,[0,4]]
data.dump('data/usdcad_lr.npy')

data = np.load('data/EUR_USD__ONE_MIN_trimmed.csv.npy')
data = data[:,[0,4]]
data.dump('data/eurusd_lr.npy')

data = np.load('data/AUD_USD__ONE_MIN_trimmed.csv.npy')
data = data[:,[0,4]]
data.dump('data/audusd_lr.npy')

data = np.load('data/GBP_USD__ONE_MIN_trimmed.csv.npy')
data = data[:,[0,4]]
data.dump('data/gbpusd_lr.npy')
"""



from matplotlib import pyplot as plt

a = np.load('data/usdcad_lr.npy')
b = np.load('data/eurusd_lr.npy')
c = np.load('data/audusd_lr.npy')
d = np.load('data/gbpusd_lr.npy')


exit()

print 'loaded'


ca=0
cb=0
cc=0
cd=0

print len(b)
print a[1,0]

na = []; nb = []; nc= []; nd = []

for i in range(len(a)):
    while a[ca,0] < b[cb,0]:
        if ca >= (len(a)-1):
            break
        ca += 1

    while c[cc,0] < b[cb,0]:
        if cc >= (len(c)-1):
            break
        cc += 1

    while d[cd,0] < b[cb,0]:
        if cd >= (len(d)-1):
            break
        cd += 1

    print ca;print cb;print cc;print cd;print '___';
    if a[ca,0] == b[cb,0] == c[cc,0] == d[cd,0]:
        na.append(a[ca])
        nb.append(b[cb])
        nc.append(c[cc])
        nd.append(d[cd])
    cb +=1
    if cb >= (len(b)-1):
        break

na = np.array(na)
nb = np.array(nb)
nc = np.array(nc)
nd = np.array(nd)
na.dump('data/usdcad_lr_common.npy')
nb.dump('data/eurusd_lr_common.npy')
nc.dump('data/audusd_lr_common.npy')
nd.dump('data/gbpusd_lr_common.npy')




#eurusd = np.load('data/eurusdBTR.npy')
#gbpusd = np.load('data/gbpusdBTR.npy')
#usdcad = np.load('data/usdcadBTR.npy')
