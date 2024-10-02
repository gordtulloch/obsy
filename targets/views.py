# targets/views.py
from django.views.generic import ListView, DetailView, DeleteView, UpdateView
from django.shortcuts import render, HttpResponseRedirect, redirect
from .models import target,simbadType,scheduleMaster,scheduleDetail
from setup.models import observatory,telescope,imager
from .forms import TargetUpdateForm, TargetImportForm
from django.urls import reverse_lazy,reverse
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse

import logging

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
        Simbad.TIMEOUT = 10 # sets the timeout to 10s
        error_message=""
        search_term = request.POST.get('search_term')
        try:
            Simbad.add_votable_fields('flux(B)', 'flux(V)', 'flux(R)', 'flux(I)','otype(main)')
            results_simbad = Simbad.query_object(search_term, wildcard=True)
            if (len(results_simbad)>0):
                df=results_simbad.to_pandas()
                results=df.to_dict('records')
                # Add results to the targets database
                for index, row in df.iterrows():
                    # Figure out the constellation
                    coords=row["RA"]+" "+row["DEC"]
                    c = SkyCoord(coords, unit=(u.hourangle, u.deg), frame='icrs')
                    
                    # Add the target record
                    target.objects.create(               
                        userId=request.user.id,
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
        except astroquery.exceptions.TableParseError as ex:
            error_message="Search Error occurred with search ("+search_term+" error: "+ex
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
        newSchedule.userId          = request.user.id
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
             

def targetUpload(request):
    if request.method == 'POST':
        form = TargetImportForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('targetUploadSuccess')
    else:
        form = TargetImportForm()
    return render(request, 'targets/target_upload.html', {'form': form})

def targetUploadSuccess(request):
    # Actually import the data
    return HttpResponse('File uploaded successfully')

