from django.core.management.base import BaseCommand, CommandError
import csv
from portvis.models import *

class Command(BaseCommand):
    help = 'load a positions file'

    def add_arguments(self, parser):
        parser.add_argument('filenm', nargs=1, type=str)

    def handle(self, *args, **options):
        # open file
        fname = options['filenm'][0]
        # file is in csv format
        with open(fname, newline='') as f:
            reader = csv.reader(f)
            # read transactions and load into db
            for row in reader:
                # create securities as needed
                try:
                    d = datetime.datetime.strptime(row[0], '%m/%d/%y').date()
                except ValueError:
                    self.stderr.write(self.style.ERROR('bad values "%s"' % row))
                    continue
                symbol = row[3]
                name = row[2]
                if not symbol and name == '-Cash-':
                    symbol = '$$'
                try:
                    s = Security.objects.get(pk=symbol)
                except Security.DoesNotExist:
                    s = Security(symbol=symbol, name=name)
                    s.save()
                # switch on type

                type = row[1]


                try:
                    if type == 'Div':
                        try:
                            value = Decimal(row[9].replace(',', ''))
                        except InvalidOperation as e:
                            self.stderr.write(self.style.ERROR('bad values "%s"' % row))
                            continue
                        t = s.transaction_set.create(tstamp=d, type=Transaction.TransactionType.DIVIDEND,
                                                     value=value,
                                                     quantity=value)
                    elif type == 'Cash':
                        try:
                            value = Decimal(row[9].replace(',', ''))
                        except InvalidOperation as e:
                            self.stderr.write(self.style.ERROR('bad values "%s"' % row))
                            continue
                        if row[5] == 'Interest Earned':
                            t = s.transaction_set.create(tstamp=d, type=Transaction.TransactionType.INTEREST,
                                                         value=value,
                                                         quantity=value)
                        else:
                            t = s.transaction_set.create(tstamp=d, type=Transaction.TransactionType.CASH,
                                                         value=value,
                                                         quantity=value)
                    elif type == 'Bought' or type == 'Sold':
                        try:
                            value = Decimal(row[9].replace(',', ''))
                        except InvalidOperation as e:
                            self.stderr.write(self.style.ERROR('bad values "%s"' % row))
                            continue
                        try:
                            quantity = Decimal(row[7].replace(',', ''))
                        except InvalidOperation as e:
                            self.stderr.write(self.style.ERROR('bad values "%s"' % row))
                            continue
                        t = s.transaction_set.create(tstamp=d, type=Transaction.TransactionType.TRADE,
                                                     value=value,
                                                     quantity=quantity)
                    elif type == 'IntInc':
                        try:
                            value = Decimal(row[9].replace(',', ''))
                        except InvalidOperation as e:
                            self.stderr.write(self.style.ERROR('bad values "%s"' % row))
                            continue
                        t = s.transaction_set.create(tstamp=d, type=Transaction.TransactionType.INTEREST,
                                                     value=value,
                                                     quantity=value)
                    elif type == 'ReinvDiv':
                        try:
                            value = Decimal(row[9].replace(',', ''))
                        except InvalidOperation as e:
                            self.stderr.write(self.style.ERROR('bad values "%s"' % row))
                            continue
                        try:
                            quantity = Decimal(row[7].replace(',', ''))
                        except InvalidOperation as e:
                            self.stderr.write(self.style.ERROR('bad values "%s"' % row))
                            continue
                        t = s.transaction_set.create(tstamp=d, type=Transaction.TransactionType.DIVIDEND,
                                                     value=value,
                                                     quantity=value)
                        t = s.transaction_set.create(tstamp=d, type=Transaction.TransactionType.TRADE,
                                                     value=value,
                                                     quantity=quantity)
                    elif type == 'CGLong' \
                            or type == 'CGShort' \
                            or type == 'XOut' \
                            or type == 'XIn' \
                            or type == 'MargInt':
                        try:
                            value = Decimal(row[9].replace(',', ''))
                        except InvalidOperation as e:
                            self.stderr.write(self.style.ERROR('bad values "%s"' % row))
                            continue
                        t = s.transaction_set.create(tstamp=d, type=Transaction.TransactionType.CASH,
                                                     value=value,
                                                     quantity=value)
                    elif type == 'StkSplit':
                        factors = row[7].split(':')
                        sin = Decimal(factors[0])
                        sout = Decimal(factors[1])
                        factor = sin/sout
                        a = s.action_set.create(tstamp=d, type=Action.ActionType.SPLIT, value=factor)

                    else:
                        self.stderr.write(self.style.ERROR('Unknown type "%s"' % row))
                except Exception as e:
                    self.stderr.write(self.style.ERROR('bad values "%s"' % row))




        self.stdout.write(self.style.SUCCESS('Successfully loaded "%s"' % options['filenm']))