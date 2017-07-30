from datetime import datetime
from dukascopyEngine import DukascopyEngine
import numpy as np
from forexSessions import forexSessions


def getHistoryIntervals(intervals, intervalSize, fileName, instrument = 'EUR/USD', period = 'ONE_MIN'):

    engine = DukascopyEngine()


    res = engine.getHistoryBars(instrument, intervalSize, 0, 0, period, trimInstrument=True, filterWeekends=False)
    for i in range(1,intervals):
        print 'collecting %d of %d' %(i, intervals)
        newData = engine.getHistoryBars(instrument, intervalSize, i*intervalSize, 0, period, trimInstrument=True, filterWeekends=False)
        res = np.append(newData, res, axis=0)
    print 'dumping to %s' %(fileName)
    res.dump(fileName)
    print 'done'

def showHistory(fileName):
    res = np.load(fileName)
    for bar in res:
        print bar

def trimFuckingHolidays(fileName):
    try:
        res = np.load(fileName+'.npy')
        print str(datetime.now()) + ' data loaded'

        newBars=[]
        for bar in res:
            dow = bar[0].weekday()#calendar.weekday(bar[0].year, bar[0].month, bar[0].day)
            if dow in [0,1,2,3]:
                newBars.append(bar)
                continue

            if dow == 4:
                if bar[0].hour > 22:
                    continue
                if bar[0].hour == 22:
                    if forexSessions.isSummerTimeInNY(bar[0]) is True:
                        continue

            if dow == 5:
                continue

            if dow == 6:
                if bar[0].hour < 21:
                    continue
                if bar[0].hour == 21:
                    if forexSessions.isSummerTimeInNY(bar[0]) is False:
                        continue

            newBars.append(bar)

        newBars = np.array(newBars)


        newBars.dump(fileName +'_trimmed.csv.npy')
    except IOError:
        print 'error'


def getHistoryIntervalsToDB(intervals, intervalSize, instrument = 'EUR/USD', period = 'ONE_MIN'):
    engine = DukascopyEngine()
    res = engine.getHistoryBars(instrument, intervalSize, 0, 0, period, trimInstrument=True, filterWeekends=False)
    for i in range(1,intervals):
        print 'collecting %d of %d' %(i, intervals)
        newData = engine.getHistoryBars(instrument, intervalSize, i*intervalSize, 0, period, trimInstrument=True, filterWeekends=False)
        res = np.append(newData, res, axis=0)
    return res

def updateQuotesFromDukascopy(instrument, period, depth = 5000000):
    intervalSize = 3000
    intervals = int(depth/intervalSize)

    import postgresql as db
    tableName = db.getTableName(instrument, period, depth)
    if db.isTableExist(tableName) is False:
        db.createQuotesTable(instrument, period, depth)
    lastQuote = db.getLastQuote(tableName)
    if lastQuote is not None:
        lastQuoteTime = lastQuote[0]
    else:
        lastQuoteTime = datetime(2000,1,1)

    lastQuoteReachedFlag = False
    engine = DukascopyEngine()
    for i in range(0, intervals):
        print 'collecting %d of %d' %(i+1, intervals)
        if lastQuoteReachedFlag is True:
            continue
        res = []
        newData = engine.getHistoryBars(instrument, intervalSize, i*intervalSize, 0, period, trimInstrument=True, filterWeekends=False)
        for row in newData:
            if row[0] > lastQuoteTime:
                res.append(row)
            else:
                lastQuoteReachedFlag = True
        db.insertQuotes(tableName, res)

def getHistoryFromDB(tableName, updateQuotesFromDB=False):
    if updateQuotesFromDB is True:
        import postgresql as db
        data = np.array(db.getAllQuotes(tableName))
        data.dump('data/'+tableName+'.npy')
        print str(datetime.now()) + ' data dumped'

    try:
        data = np.load('data/'+tableName + '.npy')
        print str(datetime.now()) + ' data loaded'
    except IOError as e:
        print e
        if updateQuotesFromDB is False:
            import postgresql as db
            data = np.array(db.getAllQuotes(tableName))
            data.dump('data/'+tableName+'.npy')
            print str(datetime.now()) + ' data dumped'
    return data


#import postgresql as db
#res = np.array(db.getAllQuotes("eurusd_1min"))
#print res[0][2]*5

#createTables()
#updateQuotes()

#exit()
#trimFuckingHolidays("/home/mage/PycharmProjects/cbTester/data/eurchf_1m_200516.csv")
#trimFuckingHolidays("/home/mage/PycharmProjects/cbTester/data/usdcad_1m_130516.csv")
#showHistory('/home/mage/PycharmProjects/cbTester/data/audusd_upto290515.csv_trimmed.csv.npy')
#getHistoryIntervals(420, 10000, '/home/mage/PycharmProjects/cbTester/data/audnzd_upto010615.csv.npy', instrument='AUD/NZD')
#getHistoryIntervals(420, 10000, '/home/mage/PycharmProjects/cbTester/data/audcad_upto010615.csv.npy', instrument='AUD/CAD')

#getHistoryIntervals(420, 10000, '/home/mage/PycharmProjects/cbTester/data/usdchf_1m_200516.csv.npy', instrument='USD/CHF', period='ONE_MIN')
#getHistoryIntervals(420, 10000, '/home/mage/PycharmProjects/cbTester/data/eurchf_1m_200516.csv.npy', instrument='EUR/CHF', period='ONE_MIN')
#getHistoryIntervals(420, 10000, '/home/mage/PycharmProjects/cbTester/data/eurusd_10s_130816.csv.npy', instrument='EUR/USD', period='TEN_SECS')