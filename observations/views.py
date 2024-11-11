from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView, DeleteView
from django.core.mail import send_mail
from django.utils import timezone
from .forms import ObservationUpdateForm, ObservationForm
from .models import observation, scheduleMaster, scheduleDetail, fitsFile, fitsSequence
from observations.models import observation
from observations.postProcess import PostProcess

import base64
import io
import matplotlib.pyplot as plt
from datetime import timedelta
from astropy import units as u
from astropy.coordinates import get_constellation
from astropy.io import fits
import numpy as np

import logging
logger = logging.getLogger("observations.views")

##################################################################################################
## observationDetailView - List observation detail with DetailView template                     ## 
##################################################################################################
class observation_detail_view(DetailView):
    model = observation
    context_object_name = "observation"
    template_name = "observations/observation_detail.html"
    login_url = "account_login"
     
##################################################################################################
## observationAllList - List all observations                                                   ## 
##################################################################################################
class observation_all_list(ListView):
    model=observation
    context_object_name="observation_list"
    template_name="observations/observation_all_list.html"
    login_url = "account_login"

##################################################################################################
## Observation Update     -  Use the UpdateView class to edit observation records               ##
##################################################################################################
class observation_update(UpdateView):
    model = observation
    form_class = ObservationForm
    template_name = "observations/observation_form.html"
    success_url = reverse_lazy('observation_all_list')
    
##################################################################################################
## Observation Delete     -  Use the DeleteView class to edit observation records               ##
##################################################################################################    
class observation_delete(DeleteView):
    model = observation
    template_name = "observations/observation_confirm_delete.html"
    success_url = reverse_lazy('observation_all_list')

##################################################################################################
## Observation create     -  Use the class to edit observation records                          ##
################################################################################################## 
def observation_create(request, target_uuid):
    if request.method == 'POST':
        form = ObservationForm(request.POST, target_uuid=target_uuid)
        if form.is_valid():
            form.save()
            return redirect('observation_all_list')
    else:
        form = ObservationForm(target_uuid=target_uuid)
    return render(request, 'observations/observation_create.html', {'form': form})

##################################################################################################
## Schedule -  this function will allow the user to create and edit a schedule of targets       ##
##################################################################################################
class schedule(ListView):
    model=scheduleMaster
    context_object_name="scheduleMaster_list"
    template_name="targets/schedule.html"
    login_url = "account_login"

##################################################################################################
## Schedule Details -  this function displays a schedule of targets                             ##
##################################################################################################
class scheduleDetails(ListView):
    model=scheduleDetail
    context_object_name="scheduleDetail_list"
    template_name="targets/schedule_detail_list.html"
    login_url = "account_login"
    
##################################################################################################
## Schedule Details Items -  this function displays individual target details                   ##
##################################################################################################
class scheduleDetailsItem(UpdateView):
    model=scheduleDetail
    context_object_name="scheduleDetailItem_list"
    template_name="targets/schedule_detail_edit.html"
    login_url = "account_login"

##################################################################################################
## buildSchedule function -  this function accepts parameters from the user and loads the       ##
##                           scheduleMaster and scheduleDetail tables with details from the     ##
##                           targets file if active=True. Then, based on the sequence provided  ##
##                           the code does a second pass through the schedule, adjusting start  ##
##                           and end times as appropriate. If the schedule lasts longer than a  ##
##                           night the targets that are after the end of twilight drop off the  ##
##                           end of the schedule to be scheduled another night.                 ##
##################################################################################################
def buildSchedule(request,start_date ,days_to_schedule,observatory_id,telescope_id,imager_id):
    # Validate inputs
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    except ValueError:
        return JsonResponse({'error': 'Invalid start_date format. Use YYYY-MM-DD.'}, status=400)

    try:
        observatory_obj = observatory.objects.get(id=observatory_id)
    except observatory.DoesNotExist:
        return JsonResponse({'error': 'Invalid observatoryId.'}, status=400)
 
    # Calculate astronomical twilight and dawn using ephem
    location = ephem.Observer()
    location.lat = str(observatory_obj.latitude)
    location.lon = str(observatory_obj.longitude)
    times = []
    for day in range(days_to_schedule):
        date = start_date + timedelta(days=day)
        location.date = date
        twilight_evening = location.next_setting(ephem.Sun(), use_center=True)
        twilight_morning = location.next_rising(ephem.Sun(), use_center=True)
        times.append((twilight_evening.datetime(), twilight_morning.datetime()))

    # Create a new scheduleMaster record
    schedule_master = scheduleMaster.objects.create(
        userId=request.user,
        schedule_date=start_date,
        schedule_days=days_to_schedule,
        observatory=observatory_obj,
        telescope=telescope.objects.get(id=telescope_id),
        imager=imager.objects.get(id=imager_id)
    )

    # Query the database and add observations to the scheduleMaster
    for twilight_evening, twilight_morning in times:
        observations = observation.objects.filter(
            observatory=observatory_id,
            telescope=telescope_id,
            imager=imager_id,
            observation_date__range=(twilight_evening, twilight_morning)
        )
        for obs in observations:
            obs_time = Time(obs.observation_date)
            obs_altaz = AltAz(obstime=obs_time, location=EarthLocation(lat=observatory_obj.latitude, lon=observatory_obj.longitude))
            obs_altitude = obs.target.transform_to(obs_altaz).alt

            if obs_altitude > 15 * u.deg:
                schedule_master.observations.add(obs)

    return JsonResponse({'scheduleMasterId': str(schedule_master.scheduleMasterId)})


def daily_observations_task(request):
    logging.info("Running daily_observations")
    # Run the post-processing task
    postProcess = PostProcess()
    postProcess.registerFitsImages()

    # Calculate the time 24 hours ago from now
    time_threshold = timezone.now() - timezone.timedelta(hours=24)
    
    # Query the fitsFile objects with fitsFileDate less than 24 hours from now
    fits_files = fitsFile.objects.filter(fitsFileDate__gte=time_threshold)
    
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

    return render(request, 'observations/email_sent.html')

class scheduleDetails(ListView):
    model=scheduleDetail
    context_object_name="scheduleDetail_list"
    template_name="targets/schedule_detail_list.html"
    login_url = "account_login"

def list_fits_files(request):
    time_filter = request.GET.get('time_filter', 'all')
    now = timezone.now()

    if time_filter == '24_hours':
        time_threshold = now - timedelta(hours=24)
    elif time_filter == '7_days':
        time_threshold = now - timedelta(days=7)
    elif time_filter == '30_days':
        time_threshold = now - timedelta(days=30)
    else:
        time_threshold = None

    if time_threshold:
        fits_files = fitsFile.objects.filter(fitsFileDate__gte=time_threshold)
    else:
        fits_files = fitsFile.objects.all()
    # Parse the filename to exclude the path
    for fits_file in fits_files:
        fits_file.fitsFileName = fits_file.fitsFileName.split('/')[-1]
    
    return render(request, 'observations/list_fits_files.html', {'fits_files': fits_files, 'time_filter': time_filter})

def fitsfile_detail(request, pk):
    fitsfile = get_object_or_404(fitsFile, pk=pk)
    
    # Get next/previous files
    all_files = list(fitsFile.objects.all().order_by('fitsFileName'))
    current_index = all_files.index(fitsfile)
    first = all_files[0]
    last = all_files[-1]
    prev_file = all_files[current_index - 1] if current_index > 0 else None
    next_file = all_files[current_index + 1] if current_index < len(all_files)-1 else None
    
    # Load FITS data
    hdul = fits.open(fitsfile.fitsFileName)
    image_data = hdul[0].data
    
    # Apply asinh stretch
    # Normalize data to 0-1 range first
    vmin = np.percentile(image_data, 1)
    vmax = np.percentile(image_data, 99)
    norm_data = (image_data - vmin) / (vmax - vmin)
    
    # Apply asinh stretch
    a = 0.1  # Adjustable parameter for stretch intensity
    stretched_data = np.arcsinh(norm_data / a) / np.arcsinh(1 / a)
    
    # Convert to displayable image
    plt.figure(figsize=(14,14))
    plt.imshow(image_data, cmap='grey', origin='lower', vmin=vmin, vmax=vmax)
    plt.axis('off')
    
    # Save plot to base64 string
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    context = {
        'fitsfile': fitsfile,
        'image_base64': image_base64,
        'first': first,
        'prev': prev_file,
        'next': next_file, 
        'last': last
    }
    return render(request, 'observations/fits_file_detail.html', context)