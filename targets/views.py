# targets/views.py
from django.views.generic import ListView, DetailView, DeleteView, UpdateView
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.conf import settings
from .models import target,simbadType
from .forms import TargetUpdateForm
from django.urls import reverse_lazy,reverse
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse

import logging
import uuid
from astroquery.simbad import Simbad
import pandas as pd
import numpy as np
from astropy.io import fits
from astropy import units as u
from astropy.coordinates import SkyCoord, get_constellation
import ephem
from datetime import datetime
import requests
import os
from PIL import Image

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
            logger.info("Searching for "+search_term)
            Simbad.add_votable_fields('flux(B)', 'flux(V)', 'flux(R)', 'flux(I)','otype(main)')
            results_simbad = Simbad.query_object(search_term, wildcard=True)
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
                        )
                    logger.info("Target added to database")
                    
                    # Add a default thumbnail from SDSS/SS for the target
                    width = 15 # Width of the image in arcmin
                    height = 15  # Height of the image in arcmin
                    
                    # Construct the URL for the STSCI Digitized Sky Survey (DSS) image
                    logger.info("Constructing URL for image")
                    url = 'https://archive.stsci.edu/cgi-bin/dss_search?r='+row["RA"]+'&d='+row["DEC"]+'&w='+str(width)+'&h='+str(height)+'&opt=GST'
                    logger.info("Requesting image "+url)

                    # Create an appropriate filename for the image
                    relative_path = os.path.join('static','images', 'thumbnails', row["MAIN_ID"].replace(' ',''))
                    jpg_filename = os.path.join(settings.BASE_DIR, relative_path)+'.jpg'
                    fits_filename = os.path.join(settings.BASE_DIR, relative_path)+'.fits'
                    logger.info("Will save image "+fits_filename+" as "+jpg_filename)

                    # Make the request to fetch the image
                    try:
                        response = requests.get(url)
                    except Exception as e:
                        logger.error("Failed to retrieve image "+fits_filename+"with error "+str(e))
                    logger.info("Response code "+str(response.status_code))

                    # Check if the request was successful
                    if response.status_code == 200:
                        with open(fits_filename, 'wb') as f:
                            f.write(response.content)
                            logger.info("Image saved as "+fits_filename)
                        # Open the FITS file and save as jpg
                        with fits.open(fits_filename) as hdul:
                            logger.info("Opened FITS file "+fits_filename)
                            # Get the image data from the primary HDU
                            image_data = hdul[0].data
                            logger.info("Got image data from FITS file")

                            # Normalize the image data to the range 0-255
                            logger.info("Normalizing image data")
                            image_data = image_data - np.min(image_data)
                            image_data = (image_data / np.max(image_data) * 255).astype(np.uint8)

                            # Convert to a PIL image
                            logger.info("Converting image to PIL")
                            image = Image.fromarray(image_data)
                            logger.info("Converted image to PIL")
                            # Save as JPG
                            logger.info("Saving image as JPG")
                            image.save(jpg_filename)

                            # Add the thumbnail to the target record
                            logger.info("Adding thumbnail to target record")
                            target_obj = target.objects.get(targetName=row["MAIN_ID"].replace(' ',''))
                            target_obj.targetThumbnail = os.path.join(relative_path)+'.jpg'

                        # Remove the temporary FITS file
                        logger.info("Removing FITS file "+fits_filename)
                        os.remove(fits_filename)
                    else:
                        logger.error("Failed to retrieve image "+fits_filename)
            else: 
                results=[]
            return redirect('target_all_list')
        except Exception as e:
            error_message="Search Error occurred with search ("+search_term+") error: "+str(e)
            logger.error(error_message)
            return render(request, 'targets/target_search.html',{'error': error_message})
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

from django.shortcuts import render
from django.http import JsonResponse
from setup.models import observatory
from targets.models import target
import ephem
from datetime import datetime, timedelta
from django.utils import timezone

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

