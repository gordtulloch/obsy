import time
import io
import tempfile
import ctypes
from datetime import datetime
from dateutil import parser
from pathlib import Path
import logging
from mcpConfig import McpConfig

import PyIndi

logger = logging.getLogger('oMCP.log')

# Most of below was borrowed from https://raw.githubusercontent.com/aaronwmorris/indi-allsky/main/indi_allsky/camera/indi.py
class IndiClient(PyIndi.BaseClient):

    __state_to_str_p = {
        PyIndi.IPS_IDLE  : 'IDLE',
        PyIndi.IPS_OK    : 'OK',
        PyIndi.IPS_BUSY  : 'BUSY',
        PyIndi.IPS_ALERT : 'ALERT',
    }

    __state_to_str_s = {
        PyIndi.ISS_OFF : 'OFF',
        PyIndi.ISS_ON  : 'ON',
    }

    __switch_types = {
        PyIndi.ISR_1OFMANY : 'ONE_OF_MANY',
        PyIndi.ISR_ATMOST1 : 'AT_MOST_ONE',
        PyIndi.ISR_NOFMANY : 'ANY',
    }

    __type_to_str = {
        PyIndi.INDI_NUMBER  : 'number',
        PyIndi.INDI_SWITCH  : 'switch',
        PyIndi.INDI_TEXT    : 'text',
        PyIndi.INDI_LIGHT   : 'light',
        PyIndi.INDI_BLOB    : 'blob',
        PyIndi.INDI_UNKNOWN : 'unknown',
    }

    __indi_interfaces = {
        PyIndi.BaseDevice.GENERAL_INTERFACE   : 'general',
        PyIndi.BaseDevice.TELESCOPE_INTERFACE : 'telescope',
        PyIndi.BaseDevice.CCD_INTERFACE       : 'ccd',
        PyIndi.BaseDevice.GUIDER_INTERFACE    : 'guider',
        PyIndi.BaseDevice.FOCUSER_INTERFACE   : 'focuser',
        PyIndi.BaseDevice.FILTER_INTERFACE    : 'filter',
        PyIndi.BaseDevice.DOME_INTERFACE      : 'dome',
        PyIndi.BaseDevice.GPS_INTERFACE       : 'gps',
        PyIndi.BaseDevice.WEATHER_INTERFACE   : 'weather',
        PyIndi.BaseDevice.AO_INTERFACE        : 'ao',
        PyIndi.BaseDevice.DUSTCAP_INTERFACE   : 'dustcap',
        PyIndi.BaseDevice.LIGHTBOX_INTERFACE  : 'lightbox',
        PyIndi.BaseDevice.DETECTOR_INTERFACE  : 'detector',
        PyIndi.BaseDevice.ROTATOR_INTERFACE   : 'rotator',
        PyIndi.BaseDevice.AUX_INTERFACE       : 'aux',
    }

    def __init__(self):
        super(IndiClient, self).__init__()

        self.config = McpConfig()
    
        self._telescope_device = None
        self._dome_device = None

        logger.info('creating an instance of IndiClient')

        pyindi_version = '.'.join((
            str(getattr(PyIndi, 'INDI_VERSION_MAJOR', -1)),
            str(getattr(PyIndi, 'INDI_VERSION_MINOR', -1)),
            str(getattr(PyIndi, 'INDI_VERSION_RELEASE', -1)),
        ))
        logger.info('PyIndi version: %s', pyindi_version)


    @property
    def disconnected(self):
        return self._disconnected

    @disconnected.setter
    def disconnected(self, new_disconnected):
        self._disconnected = bool(new_disconnected)

    @property
    def telescope_device(self):
        return self._telescope_device

    @telescope_device.setter
    def telescope_device(self, new_telescope_device):
        self._telescope_device = new_telescope_device

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, new_timeout):
        self._timeout = float(new_timeout)

    @property
    def filename_t(self):
        return self._filename_t

    @filename_t.setter
    def filename_t(self, new_filename_t):
        self._filename_t = str(new_filename_t)

    def newDevice(self, d):
        logger.info("new device %s", d.getDeviceName())

    def removeDevice(self, d):
        logger.info("remove device %s", d.getDeviceName())


    def newProperty(self, p):
        #logger.info("new property %s for %s", p.getName(), p.getDeviceName())
        pass

    def removeProperty(self, p):
        logger.info("remove property %s for %s", p.getName(), p.getDeviceName())


    def updateProperty(self, p):
        # INDI 2.x.x code path

        if hasattr(PyIndi.BaseMediator, 'newNumber'):
            # indi 1.9.9 has a bug that will run both the new an old code paths for properties
            return

        if p.getType() == PyIndi.INDI_BLOB:
            p_blob = PyIndi.PropertyBlob(p)
            #logger.info("new Blob %s for %s", p_blob.getName(), p_blob.getDeviceName())
            self.processBlob(p_blob[0])
        elif p.getType() == PyIndi.INDI_NUMBER:
            #p_number = PyIndi.PropertyNumber(p)
            #logger.info("new Number %s for %s", p_number.getName(), p_number.getDeviceName())
            pass
        elif p.getType() == PyIndi.INDI_SWITCH:
            #p_switch = PyIndi.PropertySwitch(p)
            #logger.info("new Switch %s for %s", p_switch.getName(), p_switch.getDeviceName())
            pass
        elif p.getType() == PyIndi.INDI_TEXT:
            #p_text = PyIndi.PropertyText(p)
            #logger.info("new Text %s for %s", p_text.getName(), p_text.getDeviceName())
            pass
        elif p.getType() == PyIndi.INDI_LIGHT:
            #p_light = PyIndi.PropertyLight(p)
            #logger.info("new Light %s for %s", p_light.getName(), p_light.getDeviceName())
            pass
        else:
            logger.warning('Property type not matched: %d', p.getType())


    def newBLOB(self, bp):
        # legacy INDI 1.x.x code path
        #logger.info("new BLOB %s", bp.name)
        self.processBlob(bp)

    def newSwitch(self, svp):
        # legacy INDI 1.x.x code path
        #logger.info("new Switch %s for %s", svp.name, svp.device)
        pass

    def newNumber(self, nvp):
        # legacy INDI 1.x.x code path
        #logger.info("new Number %s for %s", nvp.name, nvp.device)
        pass

    def newText(self, tvp):
        # legacy INDI 1.x.x code path
        #logger.info("new Text %s for %s", tvp.name, tvp.device)
        pass

    def newLight(self, lvp):
        # legacy INDI 1.x.x code path
        #logger.info("new Light %s for %s", lvp.name, lvp.device)
        pass

    def newMessage(self, d, m):
        logger.info("new Message %s", d.messageQueue(m))

    def serverConnected(self):
        logger.info("Server connected (%s:%d)", self.getHost(), self.getPort())

        self.disconnected = False

    def serverDisconnected(self, code):
        logger.info("Server disconnected (exit code = %d, %s, %d", code, str(self.getHost()), self.getPort())

        self.disconnected = True

    def parkTelescope(self):
        if not self.telescope_device:
            return

        logger.info('Parking telescope')

        park_config = {
            'SWITCHES' : {
                'TELESCOPE_PARK' : {
                    'on'  : ['PARK'],
                    'off' : ['UNPARK'],
                },
            }
        }

        self.configureTelescopeDevice(park_config)


    def unparkTelescope(self):
        if not self.telescope_device:
            return

        logger.info('Unparking telescope')

        unpark_config = {
            'SWITCHES' : {
                'TELESCOPE_PARK' : {
                    'on'   : ['UNPARK'],
                    'off'  : ['PARK'],
                },
            }
        }

        self.configureTelescopeDevice(unpark_config)


    def setTelescopeParkPosition(self, ra, dec):
        if not self.telescope_device:
            return

        logger.info('Setting telescope park position to RA %0.2f, Dec %0.2f', ra, dec)

        park_pos = {
            'PROPERTIES' : {
                'TELESCOPE_PARK_POSITION' : {
                    'PARK_HA'  : float(ra),
                    'PARK_DEC' : float(dec),
                },
            },
        }


        self.configureTelescopeDevice(park_pos)


    def disableDebug(self, ccd_device):
        debug_config = {
            "SWITCHES" : {
                "DEBUG" : {
                    "on"  : ["DISABLE"],
                    "off" : ["ENABLE"],
                },
            }
        }

        self.configureDevice(ccd_device, debug_config)


    def disableDebugCcd(self):
        self.disableDebug(self.ccd_device)


    def getDeviceProperties(self, device):
        properties = dict()

        ### Causing a segfault as of 8/25/22
        #for p in device.getProperties():
        #    name = p.getName()
        #    properties[name] = dict()

        #    if p.getType() == PyIndi.INDI_TEXT:
        #        for t in p.getText():
        #            properties[name][t.getName()] = t.getText()
        #    elif p.getType() == PyIndi.INDI_NUMBER:
        #        for t in p.getNumber():
        #            properties[name][t.getName()] = t.getValue()
        #    elif p.getType() == PyIndi.INDI_SWITCH:
        #        for t in p.getSwitch():
        #            properties[name][t.getName()] = self.__state_to_str_s[t.getState()]
        #    elif p.getType() == PyIndi.INDI_LIGHT:
        #        for t in p.getLight():
        #            properties[name][t.getName()] = self.__state_to_str_p[t.getState()]
        #    elif p.getType() == PyIndi.INDI_BLOB:
        #        pass
        #        #for t in p.getBLOB():
        #        #    logger.info("       %s(%s) = %d bytes", t.name, t.label, t.size)

        #logger.warning('%s', pformat(properties))

        return properties

    def _findTelescopes(self):
        logger.info('Searching for available telescopes/mounts')

        telescope_list = list()

        for device in self.getDevices():
            logger.info('Found device %s', device.getDeviceName())
            device_interfaces = self.findDeviceInterfaces(device)

            for k, v in self.__indi_interfaces.items():
                if device_interfaces & k:
                    if k == PyIndi.BaseDevice.TELESCOPE_INTERFACE:
                        logger.info(' Detected %s', device.getDeviceName())
                        telescope_list.append(device)

        return telescope_list


    def findTelescope(self, telescope_name='Telescope Simulator'):
        telescope_list = self._findTelescopes()

        logger.info('Found %d Telescopess', len(telescope_list))

        for t in telescope_list:
            if t.getDeviceName().lower() == telescope_name.lower():
                self.telescope_device = t
                break
        else:
            logger.error('No telescopes found')

        return self.telescope_device

    def configureDevice(self, device, indi_config, sleep=1.0):
        ### Configure Device Switches
        for k, v in indi_config.get('SWITCHES', {}).items():
            logger.info('Setting switch %s', k)
            self.set_switch(device, k, on_switches=v.get('on', []), off_switches=v.get('off', []))

        ### Configure Device Properties
        for k, v in indi_config.get('PROPERTIES', {}).items():
            logger.info('Setting property (number) %s', k)
            self.set_number(device, k, v)

        ### Configure Device Text
        for k, v in indi_config.get('TEXT', {}).items():
            logger.info('Setting property (text) %s', k)
            self.set_text(device, k, v)


        # Sleep after configuration
        time.sleep(sleep)

    def configureTelescopeDevice(self, *args, **kwargs):
        if not self.telescope_device:
            logger.warning('No telescope to configure')
            return

        self.configureDevice(self.telescope_device, *args, **kwargs)

    def getTelescopeRaDec(self):
        if not self.telescope_device:
            return self.ra_v.value, self.dec_v.value

        try:
            equatorial_eod_coord = self.get_control(self.telescope_device, 'EQUATORIAL_EOD_COORD', 'number', timeout=0.5)
        except TimeOutException:
            return self.ra_v.value, self.dec_v.value

        ra = float(equatorial_eod_coord[0].getValue())   # RA
        dec = float(equatorial_eod_coord[1].getValue())  # DEC

        logger.info("Telescope Coord: RA %0.2f, Dec %0.2f", ra, dec)

        return ra, dec

    # Most of below was borrowed from https://github.com/GuLinux/indi-lite-tools/blob/master/pyindi_sequence/device.py
    def get_control(self, device, name, ctl_type, timeout=None):
        if timeout is None:
            timeout = self._timeout

        ctl = None
        attr = {
            'number'  : 'getNumber',
            'switch'  : 'getSwitch',
            'text'    : 'getText',
            'light'   : 'getLight',
            'blob'    : 'getBLOB'
        }[ctl_type]

        started = time.time()
        while not ctl:
            ctl = getattr(device, attr)(name)

            if not ctl and 0 < timeout < time.time() - started:
                raise TimeOutException('Timeout finding control {0}'.format(name))

            time.sleep(0.1)

        return ctl


    def set_number(self, device, name, values, sync=True, timeout=None):
        #logger.info('Name: %s, values: %s', name, str(values))
        c = self.get_control(device, name, 'number')

        if c.getPermission() == PyIndi.IP_RO:
            logger.error('Number control %s is read only', name)
            return c

        for control_name, index in self.__map_indexes(c, values.keys()).items():
            logger.info('Setting %s = %s', c[index].getLabel(), str(values[control_name]))
            c[index].setValue(values[control_name])

        self.sendNewNumber(c)

        if sync:
            self.__wait_for_ctl_statuses(c, timeout=timeout)

        return c


    def set_switch(self, device, name, on_switches=[], off_switches=[], sync=True, timeout=None):
        c = self.get_control(device, name, 'switch')

        if c.getPermission() == PyIndi.IP_RO:
            logger.error('Switch control %s is read only', name)
            return c

        is_exclusive = c.getRule() == PyIndi.ISR_ATMOST1 or c.getRule() == PyIndi.ISR_1OFMANY
        if is_exclusive :
            on_switches = on_switches[0:1]
            off_switches = [s.getName() for s in c if s.getName() not in on_switches]

        for index in range(0, len(c)):
            current_state = c[index].getState()
            new_state = current_state

            if c[index].getName() in on_switches:
                logger.info('Enabling %s (%s)', c[index].getLabel(), c[index].getName())
                new_state = PyIndi.ISS_ON
            elif is_exclusive or c[index].getName() in off_switches:
                new_state = PyIndi.ISS_OFF

            c[index].setState(new_state)

        self.sendNewSwitch(c)

        return c


    def set_text(self, device, name, values, sync=True, timeout=None):
        c = self.get_control(device, name, 'text')

        if c.getPermission() == PyIndi.IP_RO:
            logger.error('Text control %s is read only', name)
            return c

        for control_name, index in self.__map_indexes(c, values.keys()).items():
            logger.info('Setting %s = %s', c[index].getLabel(), str(values[control_name]))
            c[index].setText(values[control_name])

        self.sendNewText(c)

        if sync:
            self.__wait_for_ctl_statuses(c, timeout=timeout)

        return c


    def values(self, device, ctl_name, ctl_type):
        return dict(map(lambda c: (c.getName(), c.getValue()), self.get_control(device, ctl_name, ctl_type)))


    def switch_values(self, device, name, ctl=None):
        return self.__control2dict(device, name, 'switch', lambda c: {'value': c.getState() == PyIndi.ISS_ON}, ctl)


    def text_values(self, device, name, ctl=None):
        return self.__control2dict(device, name, 'text', lambda c: {'value': c.getText()}, ctl)


    def number_values(self, device, name, ctl=None):
        return self.__control2dict(device, name, 'text', lambda c: {'value': c.getValue(), 'min': c.min, 'max': c.max, 'step': c.step, 'format': c.format}, ctl)


    def light_values(self, device, name, ctl=None):
        return self.__control2dict(device, name, 'light', lambda c: {'value': self.__state_to_str_p[c.getState()]}, ctl)


    def ctl_ready(self, ctl, statuses=[PyIndi.IPS_OK, PyIndi.IPS_IDLE]):
        if not ctl:
            return True, 'unset'

        state = ctl.getState()

        ready = state in statuses
        state_str = self.__state_to_str_p.get(state, 'UNKNOWN')

        return ready, state_str


    def __wait_for_ctl_statuses(self, ctl, statuses=[PyIndi.IPS_OK, PyIndi.IPS_IDLE], timeout=None):
        started = time.time()

        if timeout is None:
            timeout = self._timeout

        while ctl.getState() not in statuses:
            #logger.info('%s/%s/%s: %s', ctl.getDeviceName(), ctl.getGroupName(), ctl.getName(), self.__state_to_str_p[ctl.getState()])
            if ctl.getState() == PyIndi.IPS_ALERT and 0.5 > time.time() - started:
                raise RuntimeError('Error while changing property {0}'.format(ctl.getName()))

            elapsed = time.time() - started

            if 0 < timeout < elapsed:
                raise TimeOutException('Timeout error while changing property {0}: elapsed={1}, timeout={2}, status={3}'.format(ctl.getName(), elapsed, timeout, self.__state_to_str_p[ctl.getState()] ))

            time.sleep(0.15)


    def __map_indexes(self, ctl, values):
        result = {}
        for i, c in enumerate(ctl):
            #logger.info('Value name: %s', c.getName())  # useful to find value names
            if c.getName() in values:
                result[c.getName()] = i
        return result


    def __control2dict(self, device, control_name, control_type, transform, control=None):
        def get_dict(element):
            dest = {'name': element.getName(), 'label': element.getLabel()}
            dest.update(transform(element))
            return dest

        control = control if control else self.get_control(device, control_name, control_type)

        return [get_dict(c) for c in control]
