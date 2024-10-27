# observations/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from observations.models import fitsFile

@shared_task
def daily_observations_task():
    # Calculate the time 24 hours ago from now
    time_threshold = timezone.now() - timezone.timedelta(hours=24)
    
    # Query the fitsFile objects with fitsFileDate less than 24 hours from now
    fits_files = fitsFile.objects.filter(fitsFileDate__gte=time_threshold)

    # TODO:
    # Calibrate new files data
    # Stack and create a sample JPG image and thumbnail to link into the email
    
    # Create a list of file names or any other relevant information
    fits_files_list = [f"{fits_file.fitsFileName} - {fits_file.fitsFileDate}" for fits_file in fits_files]
    
    # Format the list into a string
    fits_files_str = "\n".join(fits_files_list)
    
    # Send the email
    send_mail(
        'Obsy: New FITS files processed last night',
        fits_files_str,
        settings.SENDER_EMAIL,  # Replace with your "from" email address
        [settings.RECIPIENT_EMAIL],  # Pull recipient email from settings
        fail_silently=False,
    )