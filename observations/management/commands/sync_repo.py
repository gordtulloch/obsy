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
        logger.info('Creating light sequences')
        # Remove existing sequence numbers from fitsFile records
        #for fitsFileRecord in fitsFile.objects.all():
        #    fitsFileRecord.fitsFileSequence = None
        #    fitsFileRecord.save()
        lightSeqCreated=postProcess.createLightSequences()
        logger.info('Creating calibration sequences')
        calSeqCreated=  postProcess.createCalibrationSequences()
        
        # Fix the fitsObject field for all FitsFile records
        logger.info('Fixing fitsObject field for all FitsFile records')
        for sequence in fitsSequence.objects.all():
            new_name = sequence.fitsSequenceObjectName.replace(' ', '').replace('_', '')
            sequence.fitsSequenceObjectName = new_name
            sequence.save()
            logger.info(f'Updated fitsSequenceObjectName for sequence ID {sequence.fitsSequenceId} to {new_name}')

        # Print a summary of all tasks performed
        #logger.info('Files registered: '+str(len(registered)))
        logger.info('Light sequences discovered: '+str(len(lightSeqCreated)))
        logger.info('Calibration sequences discovered: '+str(len(calSeqCreated)))
        
        self.stdout.write(self.style.SUCCESS('Successfully synchronized FITS files in the repo and saved database records. See log for details.'))