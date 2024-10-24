# targets/views.py
from django.views.generic import ListView, DetailView, DeleteView, UpdateView
from django.shortcuts import render, HttpResponseRedirect, redirect
from .models import target,simbadType
from .forms import TargetUpdateForm
from django.urls import reverse_lazy,reverse
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse

import logging
import uuid

import astroquery
from astroquery.simbad import Simbad
import pandas as pd
from astropy import units as u
from astropy.coordinates import SkyCoord, get_constellation
import ephem
from datetime import datetime

logger = logging.getLogger("targets.views")

##################################################################################################
## targetDetailView - List target detail with DetailView template                               ## 
##################################################################################################
class target_detail_view(DetailView):
    model = target
    context_object_name = "target"
    template_name = "targets/target_detail.html"
    login_url = "account_login"
     
##################################################################################################
## targetAllList - List all targets                                                             ## 
##################################################################################################
class target_all_list(ListView):
    model=target
    context_object_name="target_list"
    template_name="targets/target_all_list.html"
    login_url = "account_login"

##################################################################################################
## assignTargetClass -  A helper function that looks up targetClass based on the label          ## 
##                      from SIMBAD                                                             ##
##################################################################################################
def assignTargetClass(targetType):
    allwithTT=simbadType.objects.filter(label=targetType)
    firstentry= simbadType.objects.first()
    if firstentry != None: 
        return firstentry.category
    else:
        logger.warning("Type "+targetType+" not found in simbadTypes table")
        return "Unknown"

##################################################################################################
## Target Query     -  Allow the user to search for objects using SimBad                        ##
##################################################################################################
def target_query(request):
    error_message=""
    if request.method == 'POST':
        Simbad.TIMEOUT = 10 # sets the timeout to 120s
        error_message=""
        search_term = request.POST.get('search_term')
        try:
            Simbad.add_votable_fields('flux(B)', 'flux(V)', 'flux(R)', 'flux(I)','otype(main)')
            results_simbad = Simbad.query_object(search_term, wildcard=True)
            if (results_simbad is not None):
                df=results_simbad.to_pandas()
                results=df.to_dict('records')
                # Add results to the targets database
                for index, row in df.iterrows():
                    # Figure out the constellation
                    coords=row["RA"]+" "+row["DEC"]
                    c = SkyCoord(coords, unit=(u.hourangle, u.deg), frame='icrs')
                    
                    # Add the target record
                    target.objects.create(
                        targetId = uuid.uuid4(),     
                        targetName = row["MAIN_ID"],
                        targetType  =row["OTYPE_main"],
                        targetClass=assignTargetClass(row["OTYPE_main"]),
                        targetRA2000 = row["RA"],
                        targetDec2000 = row["DEC"],
                        targetConst = get_constellation(c),
                        targetMag = row["FLUX_V"],
                        )
            else: 
                results=[]
            return render(request, 'targets/target_result.html',{'results': results})
        except Exception as e:
            error_message="Search Error occurred with search ("+search_term+")"
            logger.error(error_message)
            return render(request, 'targets/target_search.html',{'error': error_message})
    else:
        return render(request, 'targets/target_search.html',{'error': error_message})
    
##################################################################################################
## Target Update     -  Use the UpdateView class to edit target records                         ##
##################################################################################################
class target_update(UpdateView):
    model = target
    form_class = TargetUpdateForm
    template_name = "targets/target_form.html"
    success_url = reverse_lazy('target_all_list')
    
##################################################################################################
## Target Delete     -  Use the DeleteView class to edit target records                         ##
##################################################################################################    
class target_delete(DeleteView):
    model = target
    template_name = "targets/target_confirm_delete.html"
    success_url = reverse_lazy('target_all_list')

from django.shortcuts import render
from django.http import JsonResponse
from setup.models import observatory
from targets.models import target
import ephem
from datetime import datetime, timedelta

def target_altitude(request, target_id):
    
    # Get target and observatory details
    target_obj = target.objects.get(targetId=target_id)
    logger.info(f"Calculating altitude for target {target_obj.targetName}")
    observatory_obj = observatory.objects.first()  # Assuming a single observatory
    logger.info(f"Calculating altitude at observatory {observatory_obj.name}")

    # Calculate astronomical twilight and dawn
    location = ephem.Observer()
    location.lat = str(observatory_obj.latitude)
    location.lon = str(observatory_obj.longitude)
    location.date = datetime.utcnow()
    twilight_evening = location.next_setting(ephem.Sun(), use_center=True)
    twilight_morning = location.next_rising(ephem.Sun(), use_center=True)

    # Calculate altitude data
    altitudes = []
    times = []
    delta = timedelta(minutes=10)
    current_time = twilight_evening.datetime()
    while current_time <= twilight_morning.datetime():
        location.date = current_time
        target_ephem = ephem.FixedBody()
        target_ephem._ra = target_obj.targetRA2000
        target_ephem._dec = target_obj.targetDec2000
        target_ephem.compute(location)
        altitudes.append(target_ephem.alt * 180.0 / ephem.pi)  # Convert radians to degrees
        times.append(current_time.isoformat())
        current_time += delta

    return JsonResponse({'times': times, 'altitudes': altitudes})

