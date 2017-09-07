import postgresql as db
from datetime import date, datetime, timedelta
from dukascopyEngine import DukascopyEngine
from dateutil.relativedelta import relativedelta
import sys
import numpy as np

instrumentsPediodStartDate = [
    #['EUR/USD', 'ONE_MIN', "01/01/2012"],
    #['AUD/USD', 'ONE_MIN', "01/01/2012"],
    #['NZD/USD', 'ONE_MIN', "01/01/2012"],
    #['AUD/NZD', 'ONE_MIN', "01/01/2012"],
    #['GBP/USD', 'ONE_MIN', "01/01/2012"],
    #['EUR/USD', 'ONE_MIN', "01/01/2007"],
    ['USD/CHF', 'ONE_MIN', "01/06/2017"],
    ['USD/JPY', 'ONE_MIN', "01/01/2012"]];
    #['EUR/USD', 'TEN_SECS', "01/01/2014"]]

def main():
    print 'started: '+ sys.argv[0] +' ' + str(datetime.utcnow())

    for instrumentPediodStartDate in instrumentsPediodStartDate:
        instrument = instrumentPediodStartDate[0]
        period = instrumentPediodStartDate[1]
        dateFrom = instrumentPediodStartDate[2]
        dateTo = (datetime.utcnow() + relativedelta(days=+1)).strftime('%d/%m/%Y')

        tableName = db.getTableName2(instrument, period, dateFrom)
        if db.isTableExist(tableName) is False:
            quotes = getHistoryDayByDay(instrument, period, dateFrom, dateTo)
            if quotes != []:
                db.createQuotesTable(tableName)
                db.insertQuotes(tableName, quotes)
            else:
                print 'no data'
        else:
            lastQuote = db.getLastQuote(tableName)
            quotes = getHistoryDayByDay(instrument, period, lastQuote[0].strftime('%d/%m/%Y %H:%M:%S'), dateTo)
            quotes = quotes[1:]#perviy cotir uzge est v baze
            db.insertQuotes(tableName, quotes)

    print 'done: ' + str(datetime.utcnow())


def getHistoryDayByDay(instrument, period, dateFromS, dateToS):
    try:
        dateFrom = datetime.strptime(dateFromS, "%d/%m/%Y %H:%M:%S")
    except Exception as e:
        dateFrom = datetime.strptime(dateFromS, "%d/%m/%Y")

    try:
        dateTo = datetime.strptime(dateToS, "%d/%m/%Y %H:%M:%S")
    except Exception as e:
        dateTo = datetime.strptime(dateToS, "%d/%m/%Y")

    engine = DukascopyEngine()
    quotes = None

    currentDate = dateFrom
    nextDay = dateFrom + relativedelta(days=+1)
    while nextDay < dateTo:
        print "collecting: " + instrument + " " + period + " " + currentDate.strftime('%d/%m/%Y %H:%M:%S') + '-' + nextDay.strftime('%d/%m/%Y %H:%M:%S')
        r = engine.getHistoryFromDateToDate(instrument, period, currentDate.strftime('%d/%m/%Y %H:%M:%S'), nextDay.strftime('%d/%m/%Y %H:%M:%S'))
        r = r[:len(r)-1] #obrezaem posledniy chtobi ne bilo gemora na sticah dnia
        if quotes is None:
            quotes = r
        else:
            quotes = np.append(quotes, r, axis=0)
        currentDate = currentDate + relativedelta(days=+1)
        nextDay = nextDay + relativedelta(days=+1)
    if currentDate < dateTo:
        print "collecting: " + instrument + " " + period + " " + currentDate.strftime('%d/%m/%Y %H:%M:%S') + '-' + nextDay.strftime('%d/%m/%Y %H:%M:%S')
        r = engine.getHistoryFromDateToDate(instrument, period, currentDate.strftime('%d/%m/%Y %H:%M:%S'), nextDay.strftime('%d/%m/%Y %H:%M:%S'))
        if quotes is None:
            quotes = r
        else:
            quotes = np.append(quotes, r, axis=0)
    return quotes



def checkIntegrity(instrumentPediodStartDate):
    instrument = instrumentPediodStartDate[0]
    period = instrumentPediodStartDate[1]
    dateFrom = instrumentPediodStartDate[2]
    td = timedelta(seconds=1)
    if period == 'ONE_MIN':
        td = timedelta(seconds=60)
    if period == 'TEN_SECS':
        td = timedelta(seconds=10)

    tableName = db.getTableName2(instrument, period, dateFrom)
    quotes = db.getAllQuotes(tableName)
    quotes = np.array(quotes)
    prevquote = quotes[0]
    print 'num of quotes: ' + str(len(quotes))
    for quote in quotes[1:]:
        if quote[0] - prevquote[0] != td:
            print '------------------------'
            print prevquote
            print quote
            print '------------------------'
        prevquote = quote

main()
#for instrumentPediodStartDate in instrumentsPediodStartDate:
#    print str(instrumentPediodStartDate) + ' checking..'
#    checkIntegrity(instrumentPediodStartDate)