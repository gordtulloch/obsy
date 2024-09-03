#############################################################################################################
## i s S U N                                                                                               ##
#############################################################################################################
# Check if the Sun is up
from pysolar.solar import *
import astropy.coordinates as coord
from astropy.time import Time
import astropy.units as u
import astropy.io.fits as pyfits
import logging
from mcpConfig import McpConfig

class McpSun:
    def __init__(self):
        self.config=McpConfig()
        self.logger = logging.getLogger('mcpSun')
        
    def isDaytime(self):
        loc = coord.EarthLocation(float(self.config.get("LONGITUDE")) * u.deg, float(self.config.get("LATITUDE")) * u.deg)
        now = Time.now()
        altaz = coord.AltAz(location=loc, obstime=now)
        sun = coord.get_sun(now).transform_to(altaz)

        if (sun.alt.degree > -6.0):
            self.logger.info("Sun is up")
            return True
        else:
            self.logger.info("Sun is down")
            return False
