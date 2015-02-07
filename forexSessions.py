import datetime

import pytz


class forexSessions():
    #summer time: last Sunday in March - last Sunday in October (gmt + 1) 7 + 1 = 8
    #winter time: all other (gmt + 0) 7 + 0 = 7
    londonOpen = 7
    londonClose = 15.30


    #summer time: Second Sunday in March - First Sunday of November (gmt - 4)
    #winter time: all other (gmt - 5)
    newYorkOpen = 13.30
    newYorkClose = 20

    #summer time: first Sunday in April - first Sunday in October (gmt + 10)
    #winter time: all other (gmt + 11)
    sydneyOpen = 22
    sydneyClose = 7

    #no summer time: (gmt + 9)
    tokyoOpen = 24
    tokyoClose = 6

    @staticmethod
    def convert2NY(date, timeZone='GMT'):
        tz = pytz.timezone(timeZone)
        dt = tz.localize(date)
        return dt.astimezone(pytz.timezone('US/Eastern'))

    @staticmethod
    def isSummerTimeInNY(time):
        if forexSessions.getUTCOffcet(time, 'US/Eastern') == datetime.timedelta(hours=-4):
            return True
        return False

    @staticmethod
    def isSummerTimeInLondon(time):
        if forexSessions.getUTCOffcet(time, 'Europe/London') == datetime.timedelta(hours=1):
            return True
        return False

    @staticmethod
    def isSummerTimeInSydney(time):
        if forexSessions.getUTCOffcet(time, 'Australia/Sydney') == datetime.timedelta(hours=10):
            return True
        return False

    @staticmethod
    def getUTCOffcet(time, timeZone):
        tz = pytz.timezone(timeZone)
        return tz.utcoffset(time)



        #if not forexSessions.isSummerTimeInNY(bar[0]):
        #    return
