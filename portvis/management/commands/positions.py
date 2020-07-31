from django.core.management.base import BaseCommand
from portvis.models import *

class Command(BaseCommand):
    help = 'get and print positions'

    def add_arguments(self, parser):
        parser.add_argument('date', nargs=1, type=str)

    def handle(self, *args, **options):
        d = datetime.datetime.strptime(options['date'][0], '%m/%d/%y')
        self.stdout.write(self.style.SUCCESS('%s' % d))
        # get position for symbols
        s = Security.objects.all()
        for sec in s:
            p = sec.position(d)
            if p != 0:
                self.stdout.write(self.style.SUCCESS('%s: %d' % (sec.symbol, p)))
