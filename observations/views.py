from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy,reverse
from django.views.generic.edit import UpdateView, DeleteView
from .forms import ObservationUpdateForm, ObservationForm
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import observation, scheduleMaster, scheduleDetail
from targets.models import target
from setup.models import observatory,telescope,imager
from observations.models import observation
import logging

from datetime import datetime, timedelta
from astropy.time import Time
from astropy.coordinates import EarthLocation, AltAz
import astroquery
from astroquery.simbad import Simbad
import pandas as pd
from astropy import units as u
from astropy.coordinates import SkyCoord, get_constellation
import ephem
from datetime import datetime
import numpy as np

logger = logging.getLogger("obsy.observations.views")

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
## Observation create     -  Use the class to edit observation records                          ##
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
'''
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
'''