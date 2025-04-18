# targets/views.py
from django.views.generic import ListView, DetailView, DeleteView, UpdateView
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .models import Target
from .forms import TargetUpdateForm,UploadFileForm
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

import plotly.graph_objs as go
import plotly.io as pio
import pandas as pd
from datetime import datetime
import logging
import uuid
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord, get_constellation
from astropy import units as u
from datetime import datetime, timedelta
import ephem
import math
import pytz
import xml.etree.ElementTree as ET

# Get an instance of a logger
logger = logging.getLogger('targets.views')

##################################################################################################
## targetDetailView - List Target detail with DetailView template                               ## 
##################################################################################################
@login_required
def target_detail_view(request, pk):
    targetObj = get_object_or_404(Target, targetId=pk) 
    
    local_tz = pytz.timezone(settings.TIME_ZONE)
    
    # Define the location (replace with actual location)
    logger.debug("Latitude: "+str(settings.LATITUDE)+" Longitude: "+str(settings.LONGITUDE)+" Elevation: "+str(settings.ELEVATION))
    observer = ephem.Observer()
    observer.lat = settings.LATITUDE  # Default latitude
    observer.lon = settings.LONGITUDE  # Default longitude
    observer.elevation = float(settings.ELEVATION)  # Default elevation
    observer.date = datetime.now(pytz.UTC)  # Current date and time in UTC

    # Set the horizon to 18 degrees below the horizon for astronomical twilight
    observer.horizon = '-18'
    logger.debug("Observer: "+str(observer)) 

    # Calculate sunrise and sunset times
    observer.horizon = '-18'
    dawn_start = observer.previous_rising(ephem.Sun(), use_center=True).datetime()
    dusk_end = observer.previous_setting(ephem.Sun(), use_center=True).datetime()
    logger.info("Daylight starts at "+str(dawn_start.replace(tzinfo=pytz.UTC).astimezone(local_tz)) \
                +" ends at "+str(dusk_end.replace(tzinfo=pytz.UTC).astimezone(local_tz)))
    
    # Convert RA and Dec to decimal degrees
    raList=targetObj.targetRA2000.split(' ')
    if len(raList) == 3:
        ra_hrs, ra_min, ra_sec = raList
    else:
        ra_hrs, ra_min = raList
        ra_sec = 0  
    ra_decimal = (float(ra_hrs) + float(ra_min)/60 + float(ra_sec)/3600) * 15
    
    decList = targetObj.targetDec2000.split(' ')
    if len(decList) == 3:
        dec_deg, dec_min, dec_sec = decList
    else:
        dec_deg, dec_min = decList
        dec_sec = 0       
    dec_decimal = float(dec_deg) + float(dec_min)/60 + float(dec_sec)/3600
    
    if ra_decimal is not None and dec_decimal is not None:
        logger.debug("RA: " + str(ra_decimal) + " Dec: " + str(dec_decimal))
    else:
        logger.error("Failed to convert RA/Dec to decimal degrees")
        return render(request, 'targets/target_detail.html', {'Target': targetObj})

    # Calculate altitude over time for the Target
    logger.info("Calculating altitude over time for Target starting at "+str(dusk_end))
    # Create a list of 100 times between dusk_start and dawn_end
    nowTime=datetime.now(pytz.UTC)
    times = pd.date_range(start=nowTime-timedelta(hours=12),end=nowTime+timedelta(hours=12), periods=24)
    logger.debug("Times in UTC: "+str(times))

    altitudes = []
    for time in times:
        observer.date = time
        currTarget = ephem.FixedBody()
        currTarget._ra = math.radians(ra_decimal)
        currTarget._dec = math.radians(dec_decimal)
        currTarget.compute(observer)
        altitudes.append(math.degrees(currTarget.alt))

    # Re-Express times in local time
    times = [time.replace(tzinfo=pytz.UTC).astimezone(local_tz) for time in times]
    logger.debug("Times in "+settings.TIME_ZONE+" :"+str(times))
    df = pd.DataFrame({'local_time': times, 'altitude': altitudes})
    logger.debug("Dataframe: "+str(df))

    # Create the plot
    fig = go.Figure()

    # Plot the altitude over local time
    fig.add_trace(go.Scatter(x=df['local_time'], y=df['altitude'], mode='lines', name='Altitude', line=dict(color='white')))

    # Set the layout
    fig.update_layout(
        plot_bgcolor='black',
        paper_bgcolor='black',
        font=dict(color='white'),
        xaxis=dict(title='Local Time', color='white'),
        yaxis=dict(title='Altitude (degrees)', color='white'),
        title=dict(text='Altitude Over Time', x=0.5, xanchor='center', font=dict(color='white'))
    )

    # Convert the plot to JSON
    graph_json = pio.to_json(fig)

    return render(request, 'targets/target_detail.html', {'Target': targetObj, 'graph_json': graph_json})

##################################################################################################
## targetAllList - List all targets                                                             ## 
##################################################################################################
from astropy.coordinates import EarthLocation, SkyCoord
from astropy.time import Time
from astropy import units as u
from astroplan import Observer, FixedTarget
from config.models import GeneralConfig
from obsy.settings import TIME_ZONE

@login_required
def target_all_list(request):
    # Get all targets
    target_data = Target.objects.all().order_by('targetName')

    # Get search and filter parameters from the request
    search_query = request.GET.get('search', '').strip()
    target_class_filter = request.GET.get('targetClass', '').strip()

    # Apply search filter if provided
    if search_query:
        target_data = target_data.filter(targetName__icontains=search_query)

    # Apply targetClass filter if provided
    if target_class_filter:  
        target_data = target_data.filter(targetClass__iexact=target_class_filter)

    return render(request, 'targets/target_all_list.html', {
        'target_data': target_data,
        'search_query': search_query,
        'target_class_filter': target_class_filter
    })

##################################################################################################
## assignTargetClass -  A helper function that looks up targetClass based on the label          ## 
##                      from SIMBAD                                                             ##
##################################################################################################
@login_required
def assignTargetClass(targetType):
    allwithTT=SimbadType.objects.filter(label=targetType)
    firstentry= SimbadType.objects.first()
    if firstentry != None: 
        return firstentry.category
    else:
        logger.info("Type "+targetType+" not found in simbadTypes table")
        return "Unknown"

##################################################################################################
## Target Query     -  Allow the user to search for objects using SimBad                        ##
##################################################################################################
@login_required
def target_query(request):
    error_message=""
    if request.method == 'POST':
        Simbad.TIMEOUT = 10 # sets the timeout to 120s
        error_message=""
        search_term = request.POST.get('search_term')
        try:
            search_term = search_term.strip()
            logger.info("Searching for "+search_term)
            Simbad.add_votable_fields('flux(B)', 'flux(V)', 'flux(R)', 'flux(I)','otype(main)')
            results_simbad = Simbad.query_object(search_term, wildcard=True)
        except Exception as e:
            logger.error("Error searching for "+search_term)
            error_message="Error searching for "+search_term
            results_simbad=None
            
        if (results_simbad is not None):
            logger.info("Search results found")
            df=results_simbad.to_pandas()
            results=df.to_dict('records')
            # Add results to the targets database
            logger.info("Adding "+str(len(df))+" targets to database")
            for index, row in df.iterrows():
                logger.info("Adding Target "+row["MAIN_ID"])
                # Figure out the constellation
                coords=row["RA"]+" "+row["DEC"]
                c = SkyCoord(coords, unit=(u.hourangle, u.deg), frame='icrs')
                
                # Add the Target record
                Target.objects.create(
                    targetId = uuid.uuid4(),     
                    targetName = row["MAIN_ID"].replace(' ',''),
                    targetType  =row["OTYPE_main"],
                    targetClass="DS",
                    targetRA2000 = row["RA"],
                    targetDec2000 = row["DEC"],
                    targetConst = get_constellation(c),
                    targetMag = row["FLUX_V"],
                    targetDefaultThumbnail = 'images/thumbnails/'+row["MAIN_ID"].replace(' ','')+'.jpg'
                    )
                logger.info("Target added to database")
        else: 
            results=[]
            return render(request, 'targets/target_search.html',{'error': error_message})
        return redirect('target_all_list')
        
    else:
        return render(request, 'targets/target_search.html',{'error': error_message})

##################################################################################################
## Target Update     -  Use the UpdateView class to edit Target records                         ##
##################################################################################################
class target_update(LoginRequiredMixin,UpdateView):
    model = Target
    form_class = TargetUpdateForm
    template_name = "targets/target_form.html"
    success_url = reverse_lazy('target_all_list')
    
##################################################################################################
## Target Delete     -  Use the DeleteView class to edit Target records                         ##
##################################################################################################    
class target_delete(LoginRequiredMixin,DeleteView):
    model = Target
    template_name = "targets/target_confirm_delete.html"
    success_url = reverse_lazy('target_all_list')

##################################################################################################
## parse_xml -  A helper function that parses an XML file and returns a list of targets         ##
##################################################################################################
def parse_xml(file):
    tree = ET.parse(file)
    root = tree.getroot()
    targets = []
    for Target in root.findall('Target'):
        target_data = {
            'targetName': Target.find('name').text,
            'targetType': Target.find('type').text,
            'targetClass': Target.find('class').text,
            'targetRA2000': Target.find('ra2000').text,
            'targetDec2000': Target.find('dec2000').text,
            'targetConst': Target.find('constellation').text,
            'targetMag': Target.find('magnitude').text,
            'targetDefaultThumbnail': Target.find('thumbnail').text,
        }
        targets.append(target_data)
    return targets

##################################################################################################
## Upload Targets    -  Allow the user to upload a file with Target data from KStars            ##
##################################################################################################
@login_required
def upload_targets_view(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            logger.info("File uploaded: "+str(file))
            tree = ET.parse(file)
            root = tree.getroot()
            for child in root:
                for subChild in child:
                    if subChild.tag == 'target':
                        for nodes in subChild:
                            if nodes.tag == 'name':
                                logger.info("Name: "+str(nodes.text))
                                Simbad.TIMEOUT = 10 # sets the timeout to 120s
                                try:
                                    search_term = str(nodes.text).strip()
                                    logger.info("Searching for "+search_term)
                                    Simbad.add_votable_fields('flux(B)', 'flux(V)', 'flux(R)', 'flux(I)','otype(main)')
                                    results_simbad = Simbad.query_object(search_term, wildcard=True)
                                except Exception as e:
                                    logger.error("Error searching for "+search_term)
                                    results_simbad=None
            
                                if (results_simbad is not None):
                                    logger.info("Search results found")
                                    df=results_simbad.to_pandas()
                                    results=df.to_dict('records')
                                    # Add results to the targets database
                                    logger.info("Adding "+str(len(df))+" targets to database")
                                    for index, row in df.iterrows():
                                        logger.info("Adding Target "+row["MAIN_ID"])
                                        try:
                                            # Figure out the constellation
                                            coords=row["RA"]+" "+row["DEC"]
                                            c = SkyCoord(coords, unit=(u.hourangle, u.deg), frame='icrs')
                                        except Exception as e:
                                            logger.error("Error getting constellation")
                                            continue

                                        # Add the Target record
                                        Target.objects.create(
                                            targetId = uuid.uuid4(),     
                                            targetName = row["MAIN_ID"].replace(' ',''),
                                            targetType  =row["OTYPE_main"],
                                            #targetClass=assignTargetClass(row["OTYPE_main"]),
                                            targetRA2000 = row["RA"],
                                            targetDec2000 = row["DEC"],
                                            targetConst = get_constellation(c),
                                            targetMag = row["FLUX_V"],
                                            targetDefaultThumbnail = 'images/thumbnails/'+row["MAIN_ID"].replace(' ','')+'.jpg'
                                            )
                                        logger.info("Target added to database")
                                else: 
                                    logger.info("Unable to add Target to the database")

            return redirect('target_all_list')
    else:
        form = UploadFileForm()
        
    return render(request, 'targets/upload_targets.html', {'form': form})

