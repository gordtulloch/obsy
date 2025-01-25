from django.core.management.base import BaseCommand
from observations.models import fitsFile, fitsSequence
from observations.postProcess import PostProcess
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Calibrate all uncalibrated files in the repo'

    def handle(self, *args, **kwargs):
        # Instantiate the PostProcess class
        postProcess = PostProcess()

        # Keep track of number of calibrated images
        calibratedImages = []

        # Find all uncalibrated files
        uncalibrated = fitsFile.objects.filter(fitsFileCalibrated=False)

        # Loop through each light frame and calibrate it
        for light_frame in uncalibrated:
            result=postProcess.calibrateFitsImage(light_frame)
            if not result:
                logger.error('Failed to calibrate file: ' + str(light_frame.fitsFileId))
            else:
                calibratedImages.append(light_frame.fitsFileId)

        self.stdout.write(self.style.SUCCESS('Successfully calibrated' + str(len(calibratedImages)) + 'files out of ' + str(len(uncalibrated)) + 'files'))
        logger.info('Successfully calibrated' + str(len(calibratedImages)) + 'files out of ' + str(len(uncalibrated)) + 'files')