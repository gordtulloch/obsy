from django.core.management.base import BaseCommand
from observations.models import fitsFile, fitsSequence
from observations.postProcess import PostProcess
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Clear existing Repo database and resync with existing files'

    def handle(self, *args, **kwargs):
        # Delete all FitsFile records
        logger.info('Deleting all existing FitsFile and FitsSequence records')
        fitsFile.objects.all().delete()
        fitsSequence.objects.all().delete()

        # Register all FITS files in the repo
        postProcess=PostProcess()
        #logger.info('Registering all FITS files in the repo')
        registered=postProcess.registerFitsImages(moveFiles=False)

        # Print a summary of all tasks performed
        logger.info('Files registered: '+str(len(registered)))
        
        self.stdout.write(self.style.SUCCESS('Successfully synchronized FITS files in the repo and saved database records. See log for details.'))