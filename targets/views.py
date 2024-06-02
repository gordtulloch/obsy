# targets/views.py
from django.views.generic import ListView, DetailView, DeleteView, UpdateView
from django.shortcuts import render, get_object_or_404, redirect
from .models import target,simbadType,scheduleMaster,scheduleFile,sequenceFile
from setup.models import observatory,telescope,imager
from .forms import TargetUpdateForm,sequenceFileForm,scheduleFileForm
from django.urls import reverse_lazy
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
## Schedule Edit List-  this function will allow the user to edit a schedule of targets if one  ##
##                      has been created using the Schedule function                            ##
##################################################################################################
class schedule_edit(ListView):
    model=scheduleMaster
    context_object_name="schedule_edit"
    template_name="targets/schedule_edit.html"
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
                        catalogIDs = row["MAIN_ID"],
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
## Schedule function -  this function will accept two inputs from the user, a start date to     ##
##                      use when  generating a schedule and a number of dates out in which to   ##
##                      plan. The result will be a list of schedule entries that are passed to  ##
##                      another view that enables the user to manipulate and save the schedule  ##
##################################################################################################
def schedule(request):
    error_message=""
    if request.method == 'POST':
        error_message=""
        start_date          = request.POST.get('start_date')
        days_to_schedule    = request.POST.get('days_to_schedule')
        observatory_id      = request.POST.get('observatory_id')
        telescope_id        = request.POST.get('telescope_id')
        imager_id           = request.POST.get('imager_id')
        
        buildSchedule(request,start_date,days_to_schedule,observatory_id,telescope_id,imager_id) # Run the routine that populates the schedule tables
        results=schedule.objects.all()
        return render(request, 'targets/schedule_edit.html',{'results': results})
    else:
        return render(request, 'targets/schedule_query.html',{'error': error_message})

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
             
##################################################################################################
## checkSchedule function -  this function looks at a past schedule and goes through each       ##
##                           detail row in the schedule to determine if the item was completed. ##
##                           If so if the target was one time then the target is marked         ##
##                           inactive otherwise it is left as active to be scheduled another    ##
##                           night.                                                             ##
##################################################################################################
def checkSchedule():
    # TODO
    return

##################################################################################################
## sequence_file_upload function - allows a user to upload a EKOS Sequence File                 ##
##################################################################################################
def sequence_file_upload(request):
    form = sequenceFileForm()
    if request.method == 'POST':
        form = sequenceFileForm(request.POST, request.FILES)
        if form.is_valid():
            # Handle the uploaded file (save its contents to a text field, for example)
            newSequence = sequenceFile() 
            newSequence.sequenceFileName = request.FILES["file"].name
            newSequence.sequenceFileData = request.FILES["file"].read().decode("utf-8")
            return HttpResponseRedirect("/success/url/")
    return render(request, "targets/sequence_upload.html", locals())
    
##################################################################################################
## sequence_list - List all targets                                                             ## 
##################################################################################################
class sequence_file_list(ListView):
    model=sequenceFile
    context_object_name="sequence_list"
    template_name="targets/sequence_file_list.html"
    login_url = "account_login"

##################################################################################################
## schedule_file_upload function - allows a user to upload a EKOS Sequence File                 ##
##################################################################################################
def schedule_file_upload(request):
    if request.method == 'POST':
        form = scheduleFileForm(request.POST, request.FILES)
        if form.is_valid():
            newSchedule = scheduleFile() 
            newSchedule.sequenceFileName = request.FILES["file"].name
            newSchedule.sequenceFileData = request.FILES["file"].read().decode("utf-8")
            return HttpResponseRedirect("/success/url/")
    else:
        form = scheduleFileForm(request)
    return render(request, "targets/schedule_upload.html", {"form": form})
    
##################################################################################################
## schedule_file_list - List all targets                                                             ## 
##################################################################################################
class schedule_file_list(ListView):
    model=scheduleFile
    context_object_name="schedule_list"
    template_name="targets/schedule_file_list.html"
    login_url = "account_login"