from django.core.management.base import BaseCommand
from portvis.models import *

class Command(BaseCommand):
    help = 'get and print positions'

    def handle(self, *args, **options):
        d1 = datetime.datetime.strptime('02/20/20', '%m/%d/%y').date()
        d2 = datetime.datetime.strptime('03/11/20', '%m/%d/%y').date()
        d3 = datetime.datetime.strptime('08/01/20', '%m/%d/%y').date()
        self.stdout.write(self.style.SUCCESS(f"Symbol:Position@{d1}:Value@{d2}:Value@{d3}"))
        s = Security.objects.all()
        for sec in s:
            # get position at d1
            p = sec.position(d1)
            if p != 0:
                # get mkt value at d2
                # get5 latest price before or equal to target date
                p1 = sec.price_set.filter(tstamp__lte=d2).order_by('-tstamp').first()
                if not p1:
                    # no price
                    self.stderr.write(self.style.ERROR(f"no price for {sec.symbol} at {d2}"))
                    p1 = Price(security=sec, tstamp=d2, close=Decimal(1))

                mkt1 = p * p1.close
                # get mkt value at d3
                p2 = sec.price_set.filter(tstamp__lte=d3).order_by('-tstamp').first()
                if not p2:
                    # no price
                    self.stderr.write(self.style.ERROR(f"no price for {sec.symbol} at {d3}"))
                    p2 = Price(security=sec, tstamp=d3, close=Decimal(1))

                mkt2 = p * p2.close
                self.stdout.write(self.style.SUCCESS(f"{sec.symbol}:{p:.4f}:{mkt1:.2f}:{mkt2:.2f}"))

