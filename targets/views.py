# targets/views.py
from django.views.generic import ListView, DetailView, DeleteView, UpdateView
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .models import target,simbadType
from .forms import TargetUpdateForm,UploadFileForm
from django.urls import reverse_lazy
from django.http import JsonResponse
from setup.models import observatory
from targets.models import target

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
import xml.etree.ElementTree as ET
from django.utils import timezone
import ephem
import math
import pytz

# Get an instance of a logger
logger = logging.getLogger('targets.views')

##################################################################################################
## targetDetailView - List target detail with DetailView template                               ## 
##################################################################################################
def target_detail_view(request, pk):
    targetObj = get_object_or_404(target, targetId=pk) 
    
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
    ra_hrs,ra_min,ra_sec = targetObj.targetRA2000.split(' ')
    ra_decimal = (float(ra_hrs) + float(ra_min)/60 + float(ra_sec)/3600) * 15
    dec_deg,dec_min,dec_sec = targetObj.targetDec2000.split(' ')
    dec_decimal = float(dec_deg) + float(dec_min)/60 + float(dec_sec)/3600  
    logger.debug("RA: "+str(ra_decimal)+" Dec: "+str(dec_decimal))

    # Calculate altitude over time for the target
    logger.info("Calculating altitude over time for target starting at "+str(dusk_end))
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

    return render(request, 'targets/target_detail.html', {'target': targetObj, 'graph_json': graph_json})

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
        logger.info("Type "+targetType+" not found in simbadTypes table")
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
                logger.info("Adding target "+row["MAIN_ID"])
                # Figure out the constellation
                coords=row["RA"]+" "+row["DEC"]
                c = SkyCoord(coords, unit=(u.hourangle, u.deg), frame='icrs')
                
                # Add the target record
                target.objects.create(
                    targetId = uuid.uuid4(),     
                    targetName = row["MAIN_ID"].replace(' ',''),
                    targetType  =row["OTYPE_main"],
                    targetClass=assignTargetClass(row["OTYPE_main"]),
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

def parse_xml(file):
    tree = ET.parse(file)
    root = tree.getroot()
    targets = []
    for target in root.findall('target'):
        target_data = {
            'targetName': target.find('name').text,
            'targetType': target.find('type').text,
            'targetClass': target.find('class').text,
            'targetRA2000': target.find('ra2000').text,
            'targetDec2000': target.find('dec2000').text,
            'targetConst': target.find('constellation').text,
            'targetMag': target.find('magnitude').text,
            'targetDefaultThumbnail': target.find('thumbnail').text,
        }
        targets.append(target_data)
    return targets

def upload_targets_view(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            targets = parse_xml(file)
            for target_data in targets:
                target.objects.create(
                    targetName=target_data['targetName'],
                    targetType=target_data['targetType'],
                    targetClass=target_data['targetClass'],
                    targetRA2000=target_data['targetRA2000'],
                    targetDec2000=target_data['targetDec2000'],
                    targetConst=target_data['targetConst'],
                    targetMag=target_data['targetMag'],
                    targetDefaultThumbnail=target_data['targetDefaultThumbnail'],
                )
            return redirect('target_all_list')
    else:
        form = UploadFileForm()
    return render(request, 'targets/upload_targets.html', {'form': form})

