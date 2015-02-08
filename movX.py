from strategy import Strategy
from order import Order
from position import Position
from trade import *
from datetime import timedelta

class movX(Strategy):
#params
    pPeriod = 15
    pLot = 1

    pRange = 0.005

    pSetupMinBars, pSetupMaxBars = 12, 48
    pEntryPeriod = 48
    pEntryDeviation = 0.0005

    pOrdersTimeStop = 80 * 15
    pPositionsTimeStop = 80 * 15

    pTargetPeriod = 40
    pDeleteOrderIfTargetReached = False

    pRoundDigits = 5
    pAtrMultiplier = 150
    pStartHour, pEndHour = 5, 18
    pStartWeekDay, pEndWeekDay = 0, 4

    pPipSize = 8.11 / 0.0001 #pip value in usd * pip size
    pCommissionPerPip = 3.15
    pDigits = 5

    optimization = False
    pictures = 0

    def onBar(self, bar):

        if (bar[0].minute == 59 or bar[0].minute == 29  or bar[0].minute == 14 or bar[0].minute == 44):
            positions = self.engine.getPositions()
            if len(positions) > 0:
                needBars = self.pTargetPeriod * self.pPeriod * 2
                data = self.engine.getHistoryBars(self.engine.data[0].name, needBars)
                periodBars = getPeriod(data, len(data) - 1, self.pTargetPeriod, self.pPeriod)
                target = round(getEma(periodBars, len(periodBars) - 1, self.pTargetPeriod), self.pDigits)

                for position in positions:
                    if(bar[0] == position.openTime):
                        continue
                    position.order.target = target




        if (bar[0].minute == 59 or bar[0].minute == 29  or bar[0].minute == 14 or bar[0].minute == 44) and\
           bar[0].hour >= self.pStartHour and bar[0].hour <= self.pEndHour and\
           bar[0].weekday() >=  self.pStartWeekDay  and bar[0].weekday() <=  self.pEndWeekDay:
            if len(self.engine.getHistoryBars(self.engine.data[0].name, 1500)) == 0:
                return

            needBars = max((self.pSetupMaxBars + 1) * self.pPeriod, self.pTargetPeriod * self.pPeriod)
            data = self.engine.getHistoryBars(self.engine.data[0].name, needBars)
            for k in range(self.pSetupMinBars * self.pPeriod, (self.pSetupMaxBars + 1) * self.pPeriod, self.pPeriod):

                if len(data) == 0:
                    return


                currentRange = getRange(data, len(data) - 1, k)


                if  currentRange > self.pRange * bar[1]:#short
                    periodBars = getPeriod(data, len(data) - 1, self.pTargetPeriod, self.pPeriod)
                    target = round(getEma(periodBars, len(periodBars) - 1, self.pTargetPeriod), self.pDigits)
                    entry = priceChanel(data, len(data) - 1, self.pEntryPeriod)[1] + self.pEntryDeviation
                    self.engine.sendOrder(Order(-1, entry, 0, target, self.pLot, self.pOrdersTimeStop,
                        self.pPositionsTimeStop, bar[0]))
                    break
                elif currentRange < -self.pRange * bar[1]:#long
                    spread = bar[8] - bar[4]
                    periodBars = getPeriod(data, len(data) - 1, self.pTargetPeriod, self.pPeriod)
                    target = round(getEma(periodBars, len(periodBars) - 1, self.pTargetPeriod), self.pDigits)
                    entry = priceChanel(data, len(data) - 1, self.pEntryPeriod)[0] - self.pEntryDeviation + spread
                    self.engine.sendOrder(Order(1, entry, 0, target, self.pLot, self.pOrdersTimeStop,
                        self.pPositionsTimeStop, bar[0]))
                    break

    def onStop(self):
        self.engine.showEquity(self.pPipSize, self.pCommissionPerPip)
