from django.core.management.base import BaseCommand, CommandError
import csv
from portvis.models import *

class Command(BaseCommand):
    help = 'load a positions file'

    def add_arguments(self, parser):
        parser.add_argument('filenm', nargs=1, type=str)

    def handle(self, *args, **options):
        # open file
        # read date
        # read positions
        # create transactions which will set position at given time to given value
        # for all listed securities
        fname = options['filenm'][0]
        # file is in csv format
        with open(fname, newline='') as f:
            reader = csv.reader(f)
            # header line is date
            datestr = next(reader)[0]
            d = datetime.datetime.strptime(datestr, '%m/%d/%y')
            for row in reader:
                # body lines: name, symbol, shares, cost
                name = row[0]
                symbol = row[1]
                if row[2]:
                    shares = Decimal(row[2].replace(',',''))
                else:
                    shares = Decimal(0)
                cost = Decimal(row[3].replace(',',''))
                # for cash position the name is -Cash- and symbol and shares are empty
                if name == '-Cash-':
                    symbol = '$$'
                    shares = cost
                # get position for symbol
                try:
                    s = Security.objects.get(pk=symbol)
                except Security.DoesNotExist:
                    # create Security
                    s = Security(name=name, symbol=symbol)
                    s.save()
                p = s.position(d)
                diff = shares - p
                if diff != 0:
                    s.transaction_set.create(tstamp=d, type=Transaction.TransactionType.TRADE, value=cost, quantity=diff)

        self.stdout.write(self.style.SUCCESS('Successfully loaded "%s"' % options['filenm']))
