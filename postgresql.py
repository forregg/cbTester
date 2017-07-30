import psycopg2
from psycopg2.extensions import AsIs

defaultConnString = "host='localhost' dbname='quotes' user='me' password='Qwerty12'"

def getTableName(instrument, period, depth = 5000000):
    instrument = instrument.replace('/','_')
    if depth != 5000000:
        return instrument +'__'+ period + '__' + str(depth)
    return instrument + '__' + period

def getTableName2(instrument, period, dateFrom):
    instrument = instrument.replace('/','_')
    dateFrom = dateFrom.replace('/','_')
    return instrument +'__'+ period + '__' + dateFrom


def createQuotesTable(tableName, connString = defaultConnString):
    try:
        conn = psycopg2.connect(connString)
        cur = conn.cursor()
        cur.execute("CREATE TABLE public.%s (dateTime TIMESTAMP,"
                    "openBid FLOAT, highBid FLOAT, lowBid FLOAT, closeBid FLOAT, volumeBid FLOAT,"
                    "openAsk FLOAT, highAsk FLOAT, lowAsk FLOAT, closeAsk FLOAT, volumeAsk FLOAT,"
                    "instrument TEXT, period TEXT);", (AsIs(tableName),))
        conn.commit()
    except Exception as e:
        print e

def insertQuotes(tableName, quotes, connString = defaultConnString):
    conn = psycopg2.connect(connString)
    cur = conn.cursor()

    s = tableName.split("__")
    instrument = s[0].replace('_','/')
    period = s[1]

    for quote in quotes:
        try:
            cur.execute("INSERT INTO public.%s VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
                (AsIs(tableName), quote[0], quote[1], quote[2], quote[3], quote[4], quote[5], quote[6], quote[7], quote[8], quote[9], quote[10], instrument, period));
        except Exception as e:
            print(e.message)

    conn.commit()

def getLastQuote(tableName, connString = defaultConnString):
    conn = psycopg2.connect(connString)
    cur = conn.cursor()

    try:
        cur.execute("SELECT * FROM public.%s order by datetime DESC LIMIT 1", [AsIs(tableName)]);
    except Exception as e:
        print(e.message)

    results = cur.fetchall()
    if len(results) > 0:
        return results[0]
    else:
        return None

def isTableExist(tableName, connString = defaultConnString):
    conn = psycopg2.connect(connString)
    cur = conn.cursor()

    try:
        cur.execute("SELECT * FROM public.%s LIMIT 10", [AsIs(tableName)]);
    except Exception as e:
        return False

    return True

def getAllQuotes(tableName, connString = defaultConnString):
    conn = psycopg2.connect(connString)
    cur = conn.cursor()

    try:
        cur.execute("SELECT * FROM public.%s order by datetime", [AsIs(tableName)]);
        #cur.execute("SELECT * FROM public.%s", [AsIs(tableName)]);
    except Exception as e:
        print(e.message)
        return None

    print 'selected'
    results = cur.fetchall()
    if len(results) > 0:
        print 'data loaded'
        return results
    else:
        return None


#createQuotesTable('eurusd','onemin',connString)