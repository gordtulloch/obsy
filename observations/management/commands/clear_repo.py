from django.core.management.base import BaseCommand
from observations.models import fitsFile, fitsSequence

class Command(BaseCommand):
    help = 'Delete all FITS records'

    def handle(self, *args, **kwargs):
        # Delete all FitsFile records
        fitsFile.objects.all().delete()
        fitsSequence.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('Successfully deleted all FITS file and sequence records'))