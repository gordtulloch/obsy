from django.core.management.base import BaseCommand
from observations.models import fitsFile, fitsSequence
from observations.postProcess import PostProcess
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Clear existing Repo database and resync with existing files'

    def handle(self, *args, **kwargs):
        # Delete all FitsFile records
        fitsFile.objects.all().delete()
        fitsSequence.objects.all().delete()

        # Register all FITS files in the repo
        postProcess=    PostProcess()
        registered=     postProcess.registerFitsImages(moveFiles=False)
        lightSeqCreated=postProcess.createLightSequences()
        calSeqCreated=  postProcess.createCalibrationSequences()
        
        logger.info(f"Registered files: {registered}")
        logger.info(f"Light sequences created: {lightSeqCreated}")
        logger.info(f"Calibration sequences created: {calSeqCreated}")
        
        # Query for fitsFile details
        registered_files = fitsFile.objects.filter(fitsFileId__in=registered).order_by('fitsFileDate')
        #calibrated_files = fitsFile.objects.filter(fitsFileId__in=calibrated)

        # Query for fitsSequence details
        light_sequences = fitsSequence.objects.filter(fitsSequenceId__in=lightSeqCreated).order_by('fitsSequenceDate')
        cal_sequences = fitsSequence.objects.filter(fitsSequenceId__in=calSeqCreated).order_by('fitsSequenceDate')
        
        # Print a summary of all tasks performed
        print('Files registered: '+str(len(registered_files)))
        print('Light sequences discovered: '+str(len(light_sequences)))
        print('Calibration sequences discovered: '+str(len(cal_sequences)))
        #print('Files calibrated: '+str(len(calibrated_files)))
        
        self.stdout.write(self.style.SUCCESS('Successfully loaded new FITS files into the repo and saved database records'))