from django.shortcuts import render, get_object_or_404, redirect
from .forms import ObservationUpdateForm, ObservationForm
from .models import observation, scheduleMaster, scheduleDetail, sequenceFile, scheduleFile
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy,reverse
from django.views.generic.edit import UpdateView, DeleteView
from .forms import ObservationUpdateForm, ObservationForm
from targets.models import target
from setup.models import observatory,telescope,imager
import logging

import astroquery
from astroquery.simbad import Simbad
import pandas as pd
from astropy import units as u
from astropy.coordinates import SkyCoord, get_constellation
import ephem
from datetime import datetime

logger = logging.getLogger("obsy")

##################################################################################################
## observationDetailView - List observation detail with DetailView template                               ## 
##################################################################################################
class observation_detail_view(DetailView):
    model = observation
    context_object_name = "observation"
    template_name = "observations/observation_detail.html"
    login_url = "account_login"
     
##################################################################################################
## observationAllList - List all observations                                                             ## 
##################################################################################################
class observation_all_list(ListView):
    model=observation
    context_object_name="observation_list"
    template_name="observations/observation_all_list.html"
    login_url = "account_login"

##################################################################################################
## Observation Update     -  Use the UpdateView class to edit observation records                         ##
##################################################################################################
class observation_update(UpdateView):
    model = observation
    form_class = ObservationUpdateForm
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
## Observation create     -  Use the class to edit observation records               ##
################################################################################################## 
def observation_create(request,target_uuid):    
    if request.method == 'POST':
        form = ObservationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('observation_all_list')  
    else:
        form = ObservationForm()
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
        # Load the appropriate objects
        observatoryToSched=observatory.objects.filter(observatoryId=observatory_id)
        telescopeToSched=telescope.objects.filter(telescopeId=telescope_id)
        imagerToSched=imager.objects.filter(imagerId=imager_id)
        
        # Wipe the schedule tables (the details will be deleted by the foerign key relationship)
        scheduleMaster.objects.delete_everything()
        
        # Create the new schedule record
        newSchedule=scheduleMaster()
        if start_date=="TONIGHT": 
            newSchedule.scheduleDate    = datetime.now()
        else:
            newSchedule.scheduleDate = ephem.Date(start_date).datetime()

        # Copy all active entries in targets that are active to the scheduleDetail table
        for targetRec in target.objects.filter(Active=True):
            detailRow             = scheduleDetail()
            detailRow.scheduleId  = newSchedule.scheduleId
            if start_date=="TONIGHT": 
                detailRow.requiredStartTime = datetime.now()
                observer.date = datetime.now().strftime('%Y-%m-%d')
            else:
                observer.date               = ephem.Date(start_date)
                detailRow.requiredStartTime = ephem.Date(start_date).datetime()
                
            # Determine start of astronomical dark
            observer            = ephem.Observer()       # Create an observer object
            observer.lon        = observatory.longitude  # Longitude in string format
            observer.lat        = observatory.latitude   # Latitude in string format
            observer.elev       = observatory.elevation  # Elevation in meters
            observer.horizon    = "-18"                  # Desired position of sun
            
            # Populate the required fields - take the defaults on most things
            detailRow.scheduledDateTime     = observer.next_setting(ephem.Sun(), use_center=True)
            detailRow.targetId              = targetRec.targetId
             

