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
        uncalibrated = fitsFile.objects.filter(fitsCalibrated=False)

        # Loop through each light frame and calibrate it
        for light_frame in uncalibrated:
            PostProcess.calibrateFitsImage(light_frame.fitsFileId)
            calibratedImages.append(light_frame.fitsFileId)

        self.stdout.write(self.style.SUCCESS('Successfully calibrated' + str(len(calibratedImages)) + 'files out of ' + str(len(uncalibrated)) + 'files'))
        logger.info('Successfully calibrated' + str(len(calibratedImages)) + 'files out of ' + str(len(uncalibrated)) + 'files')