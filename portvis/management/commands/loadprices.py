from django.core.management.base import BaseCommand
from portvis.models import *
import numpy
import yfinanceng as yf

class Command(BaseCommand):
    help = 'get and print positions'

    def handle(self, *args, **options):
        secs = []
        s = Security.objects.all()
        secs = [j.symbol for j in s]
        symlist = " ".join(secs)
        data = yf.download(tickers=symlist, period='5y', interval='1d', group_by='ticker')
        for sec in s:
            try:
                series = data[sec.symbol]['Close']
            except KeyError:
                continue
            for tstamp, close in series.items():
                if not numpy.isnan(close):
                    try:
                        p = sec.price_set.get(tstamp=tstamp.date())
                        p.close = close
                        p.save()
                        self.stdout.write(self.style.SUCCESS(f"updated price {sec.symbol}:{tstamp}:{close}"))
                    except Price.DoesNotExist:
                        p = sec.price_set.create(tstamp=tstamp.date(), close=close)
                        self.stdout.write(self.style.SUCCESS(f"Loaded price {sec.symbol}:{tstamp}:{close}"))
        self.stdout.write(self.style.SUCCESS('Loaded prices'))
