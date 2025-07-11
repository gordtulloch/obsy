from django.conf import settings
from obsy import config
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView,CreateView
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView, DeleteView
from django.core.mail import send_mail
from django.utils import timezone
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from .forms import ObservationDSForm, SequenceFileForm, ScheduleMasterForm
from .models import Observation, scheduleMaster,fitsFile,scheduleDetail,sequenceFile,fitsSequence
from targets.models import Target
from setup.models import observatory,telescope,imager
from observations.models import Observation
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
## observationDetailView - List Observation detail with DetailView template                     ## 
##################################################################################################
class observation_detail_view(LoginRequiredMixin,DetailView):
    model = Observation
    context_object_name = "Observation"
    template_name = "observations/observation_detail.html"
    login_url = "account_login"
     
##################################################################################################
## observationAllList - List all observations                                                   ## 
##################################################################################################
class observation_all_list(LoginRequiredMixin,ListView):
    model=Observation
    context_object_name="observation_list"
    template_name="observations/observation_all_list.html"
    login_url = "account_login"

def get_queryset(self):
        return Observation.objects.select_related('sequenceFileId').all()

##################################################################################################
## Observation Update     -  Use the UpdateView class to edit Observation records               ##
##################################################################################################
@login_required
def observation_update(request, pk):
    observationObj = get_object_or_404(Observation, pk=pk)
    # Get the target object
    targetObj = get_object_or_404(Target, targetId=observationObj.targetId)
    if targetObj.targetClass == 'DS':
        form = ObservationDSForm(request.POST or None)
        template = 'observations/observation_form_ds.html'
    else:
        return HttpResponse("Invalid target class", status=400)

    if request.method == 'POST' and form.is_valid():
        observationObj = form.save(commit=False)
        observationObj.target = targetObj
        observationObj.save()
        return redirect('observation_all_list')

    return render(request, template, {'form': form})
    
####################################################################################################
## Observation UpdateDS     -  Use the UpdateView class to edit Observation records for DSO class ##
####################################################################################################
class observation_updateDS(LoginRequiredMixin,UpdateView):
    model = Observation
    form_class = ObservationDSForm
    template_name = "observations/observation_form_ds.html"
    success_url = reverse_lazy('observation_all_list')

##################################################################################################
## Observation Delete     -  Use the DeleteView class to edit Observation records               ##
##################################################################################################    
@login_required
def observation_delete(request, pk):
    logger.info(f"Deleting observation with pk: {pk}")
    observation = get_object_or_404(Observation, pk=pk)
    observation.delete()
    messages.success(request, "Observation deleted successfully.")
    return redirect('observation_all_list')

##################################################################################################
## Observation create     -  Use the class to edit Observation records                          ##
################################################################################################## 
@login_required
def observation_create(request, target_uuid=None, target_name=None):
    if request.method == 'POST':
        form = ObservationDSForm(request.POST, target_uuid=target_uuid, target_name=target_name)
        if form.is_valid():
            form.save()
            return redirect('observation_all_list')
    else:
        form = ObservationDSForm(target_uuid=target_uuid, target_name=target_name)
    return render(request, 'observations/observation_form.html', {'form': form})

##################################################################################################
## ScheduleCreateView -  Use the CreateView class to create a schedule of targets               ##
##################################################################################################
class ScheduleCreateView(LoginRequiredMixin,CreateView):
    model = scheduleMaster
    form_class = ScheduleMasterForm
    template_name = 'observations/schedule_create.html'
    success_url = reverse_lazy('schedule_list')

##################################################################################################
## Schedule -  this function will allow the user to create and edit a schedule of targets       ##
##################################################################################################
class scheduleMasterList(LoginRequiredMixin,ListView):
    model=scheduleMaster
    context_object_name="scheduleMaster_list"
    template_name="observations/schedule_list.html"
    login_url = "account_login"

##################################################################################################
## Schedule Master Update -  this function allows the user to update a schedule                 ##
##################################################################################################
class ScheduleUpdateView(LoginRequiredMixin,UpdateView):
    model = scheduleMaster
    form_class = ScheduleMasterForm
    template_name = 'observations/schedule_edit.html'
    success_url = '/observations/schedule/'

##################################################################################################
## Schedule Delete -  this function allows the user to delete a schedule                        ##
##################################################################################################
class ScheduleDeleteView(LoginRequiredMixin,DeleteView):
    model = scheduleMaster
    template_name = 'observations/schedule_confirm_delete.html'
    success_url = reverse_lazy('schedule_list')

##################################################################################################
## Schedule Download -  Produce a file on disk and send to user                                 ##
##################################################################################################
import csv
def ScheduleDownload(request, pk):
    scheduleMasterObj = get_object_or_404(scheduleMaster, pk=pk)
    scheduleDetailObj = scheduleDetail.objects.filter(scheduleMasterId=scheduleMasterObj)
    
    # For now Create a CSV file
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="ekos_schedule_{scheduleMasterObj.scheduleDate.strftime('%Y-%m-%d')}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Target Name', 'Start Time', 'End Time', 'Telescope', 'Imager'])
    
    for detail in scheduleDetailObj:
        writer.writerow([detail.targetName, detail.startTime, detail.endTime, detail.telescopeId, detail.imagerId])
    
    return response

##################################################################################################
## buildSchedule functions -  this function accepts parameters from the user and loads the      ##
##                           scheduleMaster and scheduleDetail tables with details from the     ##
##                           targets file if active=True. Then, based on the sequence provided  ##
##                           the code does a second pass through the schedule, adjusting start  ##
##                           and end times as appropriate. If the schedule lasts longer than a  ##
##                           night the targets that are after the end of twilight drop off the  ##
##                           end of the schedule to be scheduled another night.                 ##
##################################################################################################
import ephem
from datetime import datetime, timedelta

def ScheduleRegen(request, pk):
    scheduleMasterObj = get_object_or_404(scheduleMaster, pk=pk)
    
    # Delete existing scheduleDetail records
    scheduleDetailObj = scheduleDetail.objects.filter(scheduleMasterId=scheduleMasterObj)
    scheduleDetailObj.delete()
    
    # Regenerate the schedule
    scheduleMasterObj.regenSchedule()
    
    # Return to the schedule detail page
    messages.success(request, "Schedule regenerated successfully.")
    return redirect('schedule_list')

##################################################################################################
# list_fits_files -  List all FITS files in the database                                        ##
##################################################################################################
@login_required
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
        fits_files = fitsFile.objects.filter(fitsFileDate__gte=time_threshold).filter(fitsFileType='Light').order_by('-fitsFileObject')
    else:
        # Get all Light files 
        fits_files = fitsFile.objects.all().filter(fitsFileType='Light').order_by('-fitsFileObject')

    # Parse the filename to exclude the path
    for fits_file in fits_files:
        fits_file.fitsFileName = fits_file.fitsFileName.split('/')[-1]
    
    return render(request, 'observations/list_fits_files.html', {'fits_files': fits_files, 'time_filter': time_filter})

##################################################################################################
## fitsfile_detail -  Display a detailed view of a FITS file                                    ##
##################################################################################################
@login_required
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
@login_required
def sequence_file_list(request):
    sequences = sequenceFile.objects.all()
    return render(request, 'observations/sequence_file_list.html', {'sequences': sequences})

##################################################################################################
## Sequence File Create -  Create a new sequence file                                           ##
##################################################################################################
@login_required
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
@login_required
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
@login_required
def sequence_file_delete(request, pk):
    sequence_instance = get_object_or_404(sequenceFile, pk=pk)
    if request.method == 'POST':
        sequence_instance.delete()
        return redirect('observations/sequence_file_list')
    return render(request, 'observations/sequence_file_confirm_delete.html', {'sequence': sequence_instance})

##################################################################################################
## Sequence File Detail -  Display a detailed view of a sequence file                           ##
##################################################################################################
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import fitsSequence
from collections import defaultdict

class FitsFileSequenceListView(ListView):
    model = fitsSequence
    template_name = 'observations/fits_file_sequence_list.html'
    context_object_name = 'fits_file_sequences'
    paginate_by = 15

    def get_queryset(self):
        sequences = fitsSequence.objects.exclude(
            fitsSequenceObjectName__in=['Dark', 'Flat', 'Bias']
        ).order_by('fitsSequenceObjectName','fitsSequenceDate','fitsSequenceTelescope','fitsSequenceImager')
        grouped_sequences = defaultdict(list)
        for sequence in sequences:
            grouped_sequences[sequence.fitsSequenceObjectName].append({
                'date': sequence.fitsSequenceDate,
                'telescope': sequence.fitsSequenceTelescope,
                'imager': sequence.fitsSequenceImager,
            })
        return list(grouped_sequences.items())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        paginator = Paginator(queryset, self.paginate_by)
        page = self.request.GET.get('page')
        fits_file_sequences = paginator.get_page(page)
        context['fits_file_sequences'] = fits_file_sequences
        return context

@login_required
def fits_sequence_detail(request, pk):
    sequence = get_object_or_404(fitsSequence, pk=pk)
    light_frames = fitsFile.objects.filter(fitsFileSequence=sequence, fitsFileType="Light")
    calibration_frames = fitsFile.objects.filter(fitsFileSequence=sequence).exclude(fitsFileType="Light")
    
    context = {
        'sequence': sequence,
        'light_frames': light_frames,
        'calibration_frames': calibration_frames,
    }
    return render(request, 'observations/fits_sequence_detail.html', context)