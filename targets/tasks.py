import settings
from datetime import datetime
from astropy.time import Time
from astropy.coordinates import EarthLocation, AltAz, get_sun
from astropy.coordinates import SkyCoord
import astropy.units as u
from .models import Exoplanet, ExoplanetFilter
import pandas as pd
from datetime import datetime
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord, FixedTarget, get_constellation
from astropy import units as u
from datetime import datetime, timedelta
from django.utils import timezone
import pytz

import logging
logger = logging.getLogger(__name__)

def calculate_rise_transit_set_times(targetObj, location):
    targets = Target.objects.all()
    target_data = []
    
     # Define the observer's location
    location = EarthLocation(lat=float(settings.LATITUDE) * u.deg, lon=float(settings.LONGITUDE) * u.deg, height=float(settings.ELEVATION) * u.m)
    observer = Observer(location=location, timezone=settings.TIME_ZONE, name="Observer")
    # Define the current time in UTC
    utc_now = datetime.now(pytz.UTC)
    time = Time(utc_now)
    # Convert RA and Dec to decimal degrees
    raList = targetObj.targetRA2000.split(' ')
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

    # Create a SkyCoord object for the target
    target_coord = SkyCoord(ra=ra_decimal * u.deg, dec=dec_decimal * u.deg, frame='icrs')
    target_fixed = FixedTarget(coord=target_coord, name=targetObj.targetName)

    # Calculate rise, transit, and set times
    local_tz = pytz.timezone(settings.TIME_ZONE)
    rise_timeJD = observer.target_rise_time(time, target_fixed, which='next')
    rise_timeUTC = rise_timeJD.to_datetime()
    transit_timeJD = observer.target_meridian_transit_time(time, target_fixed, which='next')
    transit_timeUTC = transit_timeJD.to_datetime()
    set_timeJD = observer.target_set_time(time, target_fixed, which='next')
    set_timeUTC = set_timeJD.to_datetime()
    
    logger.info("Object name: "+targetObj.targetName)
    logger.info("rise type"+str(type(rise_timeUTC)))
    logger.info("transit type"+str(type(transit_timeUTC)))
    logger.info("set type"+str(type(set_timeUTC))) 
        
    # Convert to local time
    if type(rise_timeUTC) == datetime:
        rise_time=rise_timeUTC.replace(tzinfo=pytz.UTC).astimezone(local_tz)
    else:
        rise_time=None
    if type(transit_timeUTC) == datetime:
        transit_time=transit_timeUTC.replace(tzinfo=pytz.UTC).astimezone(local_tz)
    else:
        transit_time=None
    if type(set_timeUTC) == datetime:
        set_time=set_timeUTC.replace(tzinfo=pytz.UTC).astimezone(local_tz)
    else:
        set_time=None
    
    target_data.append({
        'Target': targetObj,
        'rise_time': rise_time,
        'transit_time': transit_time,
        'set_time': set_time
    })
    return rise_time.iso, transit_time.iso, set_time.iso

def update_exoplanet_table():
    location = EarthLocation(lat=settings.LATITUDE * u.deg, lon=settings.LONGITUDE * u.deg)
    min_altitude = settings.LATITUDE - 90 + ExoplanetFilter.min_altitude

    for target in Exoplanet.objects.all():
        if target.dec > min_altitude:
            rise_time, transit_time, set_time = calculate_rise_transit_set_times(target, location)
            target.rise_time = rise_time
            target.transit_time = transit_time
            target.set_time = set_time
            target.save()