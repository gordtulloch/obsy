from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView,CreateView
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView, DeleteView
from django.core.mail import send_mail
from django.utils import timezone
from django.http import HttpResponse

from .forms import ObservationForm,ObservationFormDS,SequenceFileForm,ScheduleMasterForm
from .models import observation, scheduleMaster,fitsFile,scheduleDetail,sequenceFile,fitsSequence
from targets.models import Target
from setup.models import observatory,telescope,imager
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
import xml.etree.ElementTree as ET
import ephem

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

def get_queryset(self):
        return observation.objects.select_related('sequenceFileId').all()

##################################################################################################
## Observation Update     -  Use the UpdateView class to edit observation records               ##
##################################################################################################
def observation_update(request, pk):
    observationObj = get_object_or_404(observation, pk=pk)
    # Get the target object
    targetObj = get_object_or_404(Target, targetId=observationObj.targetId)
    if targetObj.targetClass == 'DS':
        form = ObservationFormDS(request.POST, target_uuid=targetObj.targetId)
        formTemplate="observations/observation_form_ds.html"
    else:
        form = ObservationForm(request.POST, target_uuid=observationObj.targetId)
        formTemplate="observations/observation_form.html"
                
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('observation_all_list')

    return render(request, formTemplate, {'form': form})
    
####################################################################################################
## Observation UpdateDS     -  Use the UpdateView class to edit observation records for DSO class ##
####################################################################################################
class observation_updateDS(UpdateView):
    model = observation
    form_class = ObservationFormDS
    template_name = "observations/observation_form_ds.html"
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
    # Get the target object
    targetObj = get_object_or_404(Target, uuid=target_uuid)
    if targetObj.targetClass == 'DS':
        form = ObservationFormDS(request.POST, target_uuid=target_uuid)
        formTemplate="observations/observation_form_ds.html"
    else:
        form = ObservationForm(request.POST, target_uuid=target_uuid)
        formTemplate="observations/observation_form.html"
                
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('observation_all_list')

    return render(request, formTemplate, {'form': form})

##################################################################################################
## ScheduleCreateView -  Use the CreateView class to create a schedule of targets               ##
##################################################################################################
class ScheduleCreateView(CreateView):
    model = scheduleMaster
    form_class = ScheduleMasterForm
    template_name = 'observations/schedule_create.html'
    success_url = reverse_lazy('schedule_list')

##################################################################################################
## Schedule -  this function will allow the user to create and edit a schedule of targets       ##
##################################################################################################
class scheduleMasterList(ListView):
    model=scheduleMaster
    context_object_name="scheduleMaster_list"
    template_name="observations/schedule_list.html"
    login_url = "account_login"

##################################################################################################
## Schedule Master Update -  this function allows the user to update a schedule                 ##
##################################################################################################
class ScheduleUpdateView(UpdateView):
    model = scheduleMaster
    form_class = ScheduleMasterForm
    template_name = 'observations/schedule_edit.html'
    success_url = '/observations/schedule/'

##################################################################################################
## Schedule Delete -  this function allows the user to delete a schedule                        ##
##################################################################################################
class ScheduleDeleteView(DeleteView):
    model = scheduleMaster
    template_name = 'observations/schedule_confirm_delete.html'
    success_url = reverse_lazy('schedule_list')

##################################################################################################
## buildSchedule function -  this function accepts parameters from the user and loads the       ##
##                           scheduleMaster and scheduleDetail tables with details from the     ##
##                           targets file if active=True. Then, based on the sequence provided  ##
##                           the code does a second pass through the schedule, adjusting start  ##
##                           and end times as appropriate. If the schedule lasts longer than a  ##
##                           night the targets that are after the end of twilight drop off the  ##
##                           end of the schedule to be scheduled another night.                 ##
##################################################################################################
import ephem
from datetime import datetime, timedelta

class ScheduleRegenView(DetailView):
    def __init__(self, start_date, days_to_schedule, observatory_id, telescope_id, imager_id):
        try:
            self.startDate = datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            logger.error("Invalid start_date")
        self.daysToSchedule = days_to_schedule
        try:
            self.observatoryObj = observatory.objects.get(id=observatory_id)
        except observatory.DoesNotExist:
            logger.error("Invalid observatory_id")
        # Load operations.currentConfig where observatory=observatory_id
        try:
            currentConfig = currentConfig.objects.get().filter(observatoryId=observatory_id)
        except currentConfig.DoesNotExist:
            logger.error("No currentConfig found")
            return
        # Load the telescope and imager objects from the currentConfig
        self.telescopeList = []
        self.imagerList = []
        for config in currentConfig:
            self.telescopeList.append(config.telescopeId)
            self.imagerList.append(config.imagerId)
 
    def regenSchedule(self):
        # Calculate astronomical twilight and dawn using ephem
        location = ephem.Observer()
        location.lat = str(self.observatoryObj.latitude)
        location.lon = str(self.observatoryObj.longitude)
        times = []
        
        for day in range(self.daysToSchedule):
            date = self.startDate + timedelta(days=day)
            location.date = date
            twilight_evening = location.next_setting(ephem.Sun(), use_center=True)
            twilight_morning = location.next_rising(ephem.Sun(), use_center=True)
            times.append((twilight_evening.datetime(), twilight_morning.datetime()))

        # Query the database and add observations to scheduleDetail records
        for twilight_evening, twilight_morning in times:
            observations = observation.objects.filter(
                observatory=self.observatoryId,
                telescope=telescope_id,
                imager=imager_id,
                observation_date__range=(twilight_evening, twilight_morning)
            )
            for obs in observations:
                obs_time = Time(obs.observation_date)
                obs_altaz = AltAz(obstime=obs_time, location=EarthLocation(lat=observatory_obj.latitude, lon=observatory_obj.longitude))
                obs_altitude = obs.Target.transform_to(obs_altaz).alt

                if obs_altitude > 15 * u.deg:
                    schedule_master.observations.add(obs)

        return

##################################################################################################
## daily_observations_task -  this function will run the daily_observations task                ##
##################################################################################################
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

##################################################################################################
# list_fits_files -  List all FITS files in the database                                        ##
##################################################################################################
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

##################################################################################################
## fitsfile_detail -  Display a detailed view of a FITS file                                    ##
##################################################################################################
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

##################################################################################################
## Sequence File List -  List all sequence files                                                ##
##################################################################################################
def sequence_file_list(request):
    sequences = sequenceFile.objects.all()
    return render(request, 'observations/sequence_file_list.html', {'sequences': sequences})

##################################################################################################
## Sequence File Create -  Create a new sequence file                                           ##
##################################################################################################
def sequence_file_create(request):
    if request.method == 'POST':
        form = SequenceFileForm(request.POST, request.FILES)
        if form.is_valid():
            xml_file = request.FILES.get('sequenceFileName')
            if not xml_file:
                return HttpResponse("No file uploaded", status=400)
            else:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                sequence_data = ET.tostring(root, encoding='unicode')
                sequence_instance = form.save(commit=False)
                sequence_instance.sequenceData = sequence_data
                sequence_instance.save()
                return redirect(reverse_lazy('sequence_file_list')) 
    else:
        form = SequenceFileForm()
    return render(request, 'observations/sequence_file_form.html', {'form': form})

##################################################################################################
## Sequence File Edit -  Edit an existing sequence file                                         ##
##################################################################################################
def sequence_file_edit(request, pk):
    sequence_instance = get_object_or_404(sequenceFile, pk=pk)
    if request.method == 'POST':
        form = SequenceFileForm(request.POST, request.FILES, instance=sequence_instance)
        if form.is_valid():
            if 'xml_file' in request.FILES:
                xml_file = request.FILES.get('xml_file')
                tree = ET.parse(xml_file)
                root = tree.getroot()
                sequence_data = ET.tostring(root, encoding='unicode')
                sequence_instance.sequenceData = sequence_data
            form.save()
            return redirect(reverse_lazy('sequence_file_list')) 
    else:
        form = SequenceFileForm(instance=sequence_instance)
    return render(request, 'observations/sequence_file_form.html', {'form': form})

##################################################################################################
## Sequence File Delete -  Delete an existing sequence file                                     ##
##################################################################################################
def sequence_file_delete(request, pk):
    sequence_instance = get_object_or_404(sequenceFile, pk=pk)
    if request.method == 'POST':
        sequence_instance.delete()
        return redirect('observations/sequence_file_list')
    return render(request, 'observations/sequence_file_confirm_delete.html', {'sequence': sequence_instance})

##################################################################################################
## taskPostProcessing -  this function will run the post-processing task                         ##
##################################################################################################
def taskPostProcessing(request):
    postProcess=    PostProcess()
    registered=     postProcess.registerFitsImages()
    lightSeqCreated=postProcess.createLightSequences()
    calSeqCreated=  postProcess.createCalibrationSequences()
    # calibrated=     postProcess.calibrateAllFitsImages()
    
    logger.info(f"Registered files: {registered}")
    logger.info(f"Light sequences created: {lightSeqCreated}")
    logger.info(f"Calibration sequences created: {calSeqCreated}")
    # logger.info(f"Calibrated files: {calibrated}")
    
    # Query for fitsFile details
    registered_files = fitsFile.objects.filter(fitsFileId__in=registered).order_by('fitsFileDate')
    # calibrated_files = fitsFile.objects.filter(fitsFileId__in=calibrated)

    # Query for fitsSequence details
    light_sequences = fitsSequence.objects.filter(fitsSequenceId__in=lightSeqCreated).order_by('fitsSequenceDate')
    cal_sequences = fitsSequence.objects.filter(fitsSequenceId__in=calSeqCreated).order_by('fitsSequenceDate')
    
    # Create a summary of all tasks performed
    summary = {
        'registered_files': registered_files,
        'light_sequences': light_sequences,
        'cal_sequences': cal_sequences,
        # 'calibrated_files': calibrated_files,
        'registered_count': len(registered),
        'light_seq_count': len(lightSeqCreated),
        'cal_seq_count': len(calSeqCreated),
        # 'calibrated_count': len(calibrated)
    }
 
    return render(request, 'observations/postProcessed.html', summary)