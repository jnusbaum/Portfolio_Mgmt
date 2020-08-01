from django.db import models
from typing import List
import datetime
from decimal import *
import logging

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
    close = models.DecimalField(decimal_places=4, max_digits=16)

    class Meta:
        unique_together = ('security', 'tstamp')


# securities
class Security(models.Model):
    symbol = models.CharField(primary_key=True, max_length=128)
    name = models.TextField(default='')

    def position(self, asoft: datetime.date) -> Decimal:
        logging.debug(f"position for {self.symbol}")
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
                    if acts[i].type == Action.ActionType.STOCK_DIVIDEND:
                        logging.debug(f"position before {position}")
                        logging.debug(f"applying STOCK_DIVIDEND {acts[i].tstamp} with value {acts[i].value}")
                        position = position + acts[i].value
                        logging.debug(f"position after {position}")
                    elif acts[i].type == Action.ActionType.SPLIT:
                        logging.debug(f"position before {position}")
                        logging.debug(f"applying SPLIT {acts[i].tstamp} with value {acts[i].value}")
                        position = position * acts[i].value
                        logging.debug(f"position after {position}")
                break
            ttime = tact.tstamp

            try:
                act = acts[y]
            except IndexError:
                # apply all remaining trans
                for i in range(x, len(tacts)):
                    if tacts[i].type == Transaction.TransactionType.TRADE:
                        logging.debug(f"position before {position}")
                        logging.debug(f"applying {tacts[i].type} {tacts[i].tstamp} with quantity {tacts[i].quantity}")
                        position = position + tacts[i].quantity
                        logging.debug(f"position after {position}")
                break
            atime = act.tstamp

            if ttime <= atime:
                # apply transaction
                if tact.type == Transaction.TransactionType.TRADE:
                    logging.debug(f"position before {position}")
                    logging.debug(f"applying {tact.type} {tact.tstamp} with quantity {tact.quantity}")
                    position = position + tact.quantity
                    logging.debug(f"position after {position}")
                x += 1
            elif atime < ttime:
                # apply action
                if act.type == Action.ActionType.STOCK_DIVIDEND:
                    logging.debug(f"position before {position}")
                    logging.debug(f"applying STOCK_DIVIDEND {act.tstamp} with value {act.value}")
                    position = position + act.value
                    logging.debug(f"position after {position}")
                elif act.type == Action.ActionType.SPLIT:
                    logging.debug(f"position before {position}")
                    logging.debug(f"applying SPLIT {act.tstamp} with value {act.value}")
                    position = position * act.value
                    logging.debug(f"position after {position}")
                y += 1

        return position


    def transactions(self, start: datetime.datetime, end: datetime.datetime) -> List[Transaction]:
        pass

    def actions(self, start: datetime.datetime, end: datetime.datetime) -> List[Action]:
        pass

    def prices(self, start: datetime.datetime, end: datetime.datetime) -> List[Price]:
        pass




