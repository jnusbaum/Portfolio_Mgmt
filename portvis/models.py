from django.db import models
from typing import List
import datetime
from decimal import *

END_TIME = datetime.datetime.max
# transactions
class Transaction(models.Model):

    class TransactionType(models.TextChoices):
        TRADE = 'TRADE'
        DIVIDEND = 'DIV'
        INTEREST = 'INT'
        CAPITAL_GAIN_DISTRIBUTION = 'CG'
        CASH = 'CASH'

    security = models.ForeignKey('Security', on_delete=models.CASCADE)
    tstamp = models.DateField()
    type = models.CharField(max_length=64,
            choices=TransactionType.choices,
            default=TransactionType.CASH)
    value = models.DecimalField(decimal_places=4, max_digits=16)
    quantity = models.DecimalField(decimal_places=6, max_digits=16)


# corporate actions
class Action(models.Model):

    class ActionType(models.TextChoices):
        STOCK_DIVIDEND = 'DIV'
        SPLIT = 'SPLIT'

    security = models.ForeignKey('Security', on_delete=models.CASCADE)
    tstamp = models.DateField()
    type = models.CharField(max_length=16,
            choices=ActionType.choices,
            default=ActionType.SPLIT)
    value = models.DecimalField(decimal_places=1, max_digits=16)


# close prices
class Price(models.Model):
    security = models.ForeignKey('Security', on_delete=models.CASCADE)
    tstamp = models.DateField()


# securities
class Security(models.Model):
    symbol = models.CharField(primary_key=True, max_length=128)
    name = models.TextField(default='')

    def position(self, asoft: datetime.date) -> Decimal:
        position = Decimal(0)
        # position is calculated as requested
        tacts = self.transaction_set.filter(tstamp__lte=asoft).order_by('tstamp')
        acts = self.action_set.filter(tstamp__lte=asoft).order_by('tstamp')
        # for each transaction or action in date order
        # if transaction:TRADE apply to position
        # if action:SPLIT apply to position
        # if action:STKDIV apply to position
        x = 0
        y = 0
        while True:
            try:
                tact = tacts[x]
            except IndexError:
                # apply all remaining actions
                for i in range(y, len(acts)):
                    if act.type == Action.ActionType.STOCK_DIVIDEND:
                        position = position + acts[i].value
                    elif act.type == Action.ActionType.SPLIT:
                        position = position * acts[i].value
                break
            ttime = tact.tstamp

            try:
                act = acts[y]
            except IndexError:
                # apply all remaining trans
                for i in range(x, len(tacts)):
                    position = position + tacts[i].quantity
                break
            atime = act.tstamp

            if ttime <= atime:
                # apply transaction
                position = position + tact.quantity
                x += 1
            elif atime < ttime:
                # apply action
                if act.type == Action.ActionType.STOCK_DIVIDEND:
                    position = position + act.value
                elif act.type == Action.ActionType.SPLIT:
                    position = position * act.value
                y += 1

        return position


    def transactions(self, start: datetime.datetime, end: datetime.datetime) -> List[Transaction]:
        pass

    def actions(self, start: datetime.datetime, end: datetime.datetime) -> List[Action]:
        pass




