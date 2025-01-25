from django.core.management.base import BaseCommand
from observations.models import fitsFile, fitsSequence
from observations.postProcess import PostProcess
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Clear existing sequence database and resync sequences with existing files'

    def handle(self, *args, **kwargs):
        # Delete all Fits Sequence records
        fitsSequence.objects.all().delete()

        # Remove existing sequence numbers from fitsFile records
        for fitsFileRecord in fitsFile.objects.all():
            fitsFileRecord.fitsFileSequence = None
            fitsFileRecord.save()

        # Register all FITS files in the repo
        postProcess=PostProcess()
        logger.info('Creating light sequences')
        lightSeqCreated=postProcess.createLightSequences()
        logger.info('Creating calibration sequences')
        calSeqCreated=  postProcess.createCalibrationSequences()
        
        # Fix the fitsObject field for all FitsSequence records
        #logger.info('Fixing fitsObject field for all FitsSequence records')
        #for sequence in fitsSequence.objects.all():
        #    new_name = sequence.fitsSequenceObjectName.replace(' ', '').replace('_', '')
        #    sequence.fitsSequenceObjectName = new_name
        #    sequence.save()
        #    logger.info(f'Updated fitsSequenceObjectName for sequence ID {sequence.fitsSequenceId} to {new_name}')

        # Print a summary of all tasks performed
        logger.info('Light sequences discovered: '+str(len(lightSeqCreated)))
        logger.info('Calibration sequences discovered: '+str(len(calSeqCreated)))
        
        self.stdout.write(self.style.SUCCESS('Successfully create sequences. See log for details.'))