# targets/views.py
from django.views.generic import ListView, DetailView, DeleteView, UpdateView
from django.shortcuts import render, redirect
from django.conf import settings
from .models import target,simbadType
from .forms import TargetUpdateForm,UploadFileForm
from django.urls import reverse_lazy
from django.http import JsonResponse
from setup.models import observatory
from targets.models import target

import logging
import uuid
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord, get_constellation
from astropy import units as u
import ephem
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from django.utils import timezone

# Get an instance of a logger
logger = logging.getLogger('targets.views')

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
                    targetRA2000 = ra_to_decimal_hours(row["RA"]),
                    targetDec2000 = dec_to_decimal_degrees(row["DEC"]),
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
    
def ra_to_decimal_hours(ra):
    """
    Convert RA from HH MM SS.SS format to decimal hours.
    
    Args:
        ra (str): RA in HH MM SS.SS format.
        
    Returns:
        float: RA in decimal hours.
    """
    parts = ra.split()
    hours = float(parts[0])
    minutes = float(parts[1])
    seconds = float(parts[2])
    
    decimal_hours = hours + (minutes / 60) + (seconds / 3600)
    return str(decimal_hours)

def dec_to_decimal_degrees(dec):
    """
    Convert DEC from DD MM SS.SS format to decimal degrees.
    
    Args:
        dec (str): DEC in DD MM SS.SS format.
        
    Returns:
        float: DEC in decimal degrees.
    """
    parts = dec.split()
    degrees = float(parts[0])
    minutes = float(parts[1])
    seconds = float(parts[2])
    
    # Handle negative degrees
    if degrees < 0:
        decimal_degrees = degrees - (minutes / 60) - (seconds / 3600)
    else:
        decimal_degrees = degrees + (minutes / 60) + (seconds / 3600)
    
    return str(decimal_degrees)

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

def convert_to_current_timezone(dt):
    # Ensure the datetime is aware (has timezone info)
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt)
    
    # Convert to the current timezone
    current_timezone_dt = timezone.localtime(dt)
    
    return current_timezone_dt

def target_altitude(request, target_id):
    logger.info(f"Calculating target altitude")
    # Get target and observatory details
    target_obj = target.objects.get(targetId=target_id)
    logger.debug(f"Calculating altitude for target {target_obj.targetName}")
    observatory_obj = observatory.objects.first()  # Assuming a single observatory
    logger.debug(f"Calculating altitude at observatory {observatory_obj.name}")

    # Calculate astronomical twilight and dawn
    location = ephem.Observer()
    logger.debug(f"Observatory details: {observatory_obj.latitude}, {observatory_obj.longitude}")
    location.lat = float(observatory_obj.latitude)
    location.lon = float(observatory_obj.longitude)
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
        times.append(convert_to_current_timezone(current_time).isoformat())
        current_time += delta
    logger.debug(f"Altitude data: {altitudes}")
    logger.debug(f"Time data: {times}")
    
    return JsonResponse({'times': times, 'altitudes': altitudes})

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

