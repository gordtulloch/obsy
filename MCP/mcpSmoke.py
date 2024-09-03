import time
import os
from datetime import datetime
from datetime import timedelta  # noqa: F401
from collections import OrderedDict
import socket
import ssl
import requests
from lxml import etree
import shapely
import logging

import mcpConstants
from mcpConfig import McpConfig

logger = logging.getLogger('mcpSmoke')

# derived from indi-allsky by Aaron Morris https://github.com/aaronwmorris/indi-allsky.git thanks Aaron!

class McpSmoke(object):

    hms_kml_base_url = 'https://satepsanone.nesdis.noaa.gov/pub/FIRE/web/HMS/Smoke_Polygons/KML/{now:%Y}/{now:%m}/hms_smoke{now:%Y}{now:%m}{now:%d}.kml'

    # folder name, rating
    hms_kml_folders = OrderedDict({
        # check from heavy to light, in order
        'Smoke (Heavy)'  : mcpConstants.SMOKE_RATING_HEAVY,
        'Smoke (Medium)' : mcpConstants.SMOKE_RATING_MEDIUM,
        'Smoke (Light)'  : mcpConstants.SMOKE_RATING_LIGHT,
    })

    def __init__(self):
        self.config = McpConfig()
        self.hms_kml_data = None
        self.latitude  = float(self.config.get("LATITUDE"))
        self.longitude = float(self.config.get("LONGITUDE"))

    def updateSmoke(self):
        if self.latitude > 0 and self.longitude < 0:
            # HMS data is only good for north western hemisphere
            try:
                smoke_rating = self.update_na_hms()
            except NoSmokeData as e:
                # Leave previous values in place
                logger.error('No smoke data: %s', str(e))
                return 'No Data'

        else:
            # all other regions report no data
            smoke_rating = mcpConstants.SMOKE_RATING_NODATA

        if smoke_rating:
            logger.info('Smoke rating: %s', mcpConstants.SMOKE_RATING_MAP_STR[smoke_rating])
        else:
            logger.warning('Smoke data not updated')
            
        return smoke_rating

    def isSmokey(self):
        smoke_rating = self.updateSmoke()
        if (smoke_rating=='Smoke (Heavy)') or (smoke_rating=='Smoke (Heavy)'):
            return True
        else:
            return False

    def update_na_hms(self):
        # this pulls data from NOAA Hazard Mapping System
        # https://www.ospo.noaa.gov/Products/land/hms.html

        now = datetime.now()
        #now = datetime.now() - timedelta(days=1)  # testing

        hms_kml_url = self.hms_kml_base_url.format(**{'now' : now})


        # allow data to be reused
        if not self.hms_kml_data:
            try:
                self.hms_kml_data = self.download_kml(hms_kml_url)
            except socket.gaierror as e:
                logger.error('Name resolution error: %s', str(e))
                self.hms_kml_data = None
            except socket.timeout as e:
                logger.error('Timeout error: %s', str(e))
                self.hms_kml_data = None
            except requests.exceptions.ConnectTimeout as e:
                logger.error('Connection timeout: %s', str(e))
                self.hms_kml_data = None
            except requests.exceptions.ConnectionError as e:
                logger.error('Connection error: %s', str(e))
                self.hms_kml_data = None
            except requests.exceptions.ReadTimeout as e:
                logger.error('Connection error: %s', str(e))
                self.hms_kml_data = None
            except ssl.SSLCertVerificationError as e:
                logger.error('Certificate error: %s', str(e))
                self.hms_kml_data = None
            except requests.exceptions.SSLError as e:
                logger.error('Certificate error: %s', str(e))
                self.hms_kml_data = None


        if not self.hms_kml_data:
            raise NoSmokeData('No KML data')

        try:
            xml_root = etree.fromstring(self.hms_kml_data)
        except etree.XMLSyntaxError as e:
            self.hms_kml_data = None  # force redownload
            raise NoSmokeData('Unable to parse XML: {0:s}'.format(str(e)))
        except ValueError as e:
            self.hms_kml_data = None  # force redownload
            raise NoSmokeData('Unable to parse XML: {0:s}'.format(str(e)))


        # look for a 1 square degree area (smoke within ~35 miles)
        location_area = shapely.Polygon((
            (float(self.longitude) - 0.5, float(self.latitude) - 0.5),
            (float(self.longitude) + 0.5, float(self.latitude) - 0.5),
            (float(self.longitude) + 0.5, float(self.latitude) + 0.5),
            (float(self.longitude) - 0.5, float(self.latitude) + 0.5),
        ))
        NS = {
            "kml" : "http://www.opengis.net/kml/2.2",
        }

        found_kml_folders = False
        for folder, rating in self.hms_kml_folders.items():
            p = ".//kml:Folder[contains(., '{0:s}')]".format(folder)
            #logger.info('Folder: %s', p)
            e_folder = xml_root.xpath(p, namespaces=NS)


            if not e_folder:
                logger.error('Folder not found: %s', folder)
                continue

            found_kml_folders = True


            for e_placemark in e_folder[0].xpath('.//kml:Placemark', namespaces=NS):
                for e_polygon in e_placemark.xpath('.//kml:Polygon', namespaces=NS):
                    e_coord = e_polygon.find(".//kml:coordinates", namespaces=NS)
                    #logger.info('   %s', pformat(e_coord.text))

                    coord_list = list()
                    for line in e_coord.text.splitlines():
                        line = line.strip()

                        if not line:
                            continue

                        #logger.info('line: %s', pformat(line))
                        p_long, p_lat, p_z = line.split(',')
                        coord_list.append((float(p_long), float(p_lat)))

                    smoke_polygon = shapely.Polygon(coord_list)

                    if location_area.intersects(smoke_polygon):
                        # first match wins
                        return rating

        if not found_kml_folders:
            # without folders, there was no data to match
            raise NoSmokeData('No folders in KML')
        return mcpConstants.SMOKE_RATING_CLEAR  # no matches should mean clear

    def download_kml(self, url):
        logger.warning('Downloading %s', url)
        r = requests.get(url, allow_redirects=True, verify=True, timeout=(15.0, 30.0))

        if r.status_code >= 400:
            logger.error('URL returned %d', r.status_code)
            return None

        return r.text.encode()

class NoSmokeData(Exception):
    pass
