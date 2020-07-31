from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'load a positions file'

    def add_arguments(self, parser):
        parser.add_argument('filenm', nargs=1, type=str)

    def handle(self, *args, **options):
        # open file
        # read prices and load into db
        # create securities as needed

        self.stdout.write(self.style.SUCCESS('Successfully loaded "%s"' % options['filenm']))