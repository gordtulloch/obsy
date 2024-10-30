# observations/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from observations.models import fitsFile
from postProcess import PostProcess

@shared_task
def daily_observations_task():
    logger = logging.getLogger('observations.tasks')
    logger.debug('This is a debug message')
    logger.info('This is an info message')
    logger.warning('This is a warning message')
    logger.error('This is an error message')
    logger.critical('This is a critical message')
    # Import any new FITS files from the last 24 hours
    postProcessObj=PostProcess()
    postProcessObj.registerFitsFiles()
    
    # Calibrate any images that have not been calibrated
    logger.info("Calibrating images")
    # calibrateImages()

    # Create thumbnail images and test stacks for the images
    logger.info("Creating thumbnails and test stacks")
    # createThumbnails()

    # Calculate the time 24 hours ago from now
    time_threshold = timezone.now() - timezone.timedelta(hours=24)
    
    # Query the fitsFile objects with fitsFileDate less than 24 hours from now
    fits_files = fitsFile.objects.filter(fitsFileDate__gte=time_threshold)
    
    # Create a list of file names or any other relevant information
    fits_files_list += [f"{fits_file.fitsFileDate} - {fits_file.fitsFileName}" for fits_file in fits_files]
    
    # Format the list into a string
    fits_files_str = "\n".join(fits_files_list)
    
    # Send the email
    logger.info("Sending email notification with "+str(len(fits_files_list))+" new FITS files")
    send_mail(
        'Obsy: New FITS files processed last night',
        fits_files_str,
        settings.SENDER_EMAIL,  # Replace with your "from" email address
        [settings.RECIPIENT_EMAIL],  # Pull recipient email from settings
        fail_silently=False,
    )