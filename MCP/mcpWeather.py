#############################################################################################################
## i s B A D W E A T H E R                                                                                 ##
#############################################################################################################
# Get local weather data from ADS-WS1
# Thanks to Evan Vander Stoep https://github.com/EvanVS/WXparser
import serial, codecs

# Set up logging
import logging
logger = logging.getLogger("oMCP")

from mcpConfig import McpConfig

class McpWeather:
    def __init__(self):
        self.debug=False
        self.config=McpConfig()
        try:
            self.ser = serial.Serial(self.config.get("WEATHERPORT"),self.config.get("WEATHERBPS"),timeout=1)
            self.ser.flush()
            packet=self.ser.readline()
        except Exception as msg:
            logger.error("getWeather error: "+str(msg))
            return False

    def isBadWeather(self):
        logger.info("Checking weather...")
        self.ser.flush()
        packet=self.ser.readline()
        header = packet[0:2]
        eom = packet[50:55]
        if header == b"!!" and eom == b"\r\n":
            if (self.debug):
                logger.debug("===================================")
                logger.debug("Packet:")
                logger.debug(packet)
                logger.debug("Data:")
                logger.debug("Wind Speed                 : "+str(int(codecs.decode(packet[2:6], 'UTF-8'), 16))) # Wind Speed (0.1 kph)
                logger.debug("Wind Direction             : "+str(int(codecs.decode(packet[6:10], 'UTF-8'), 16))) # Wind Direction (0-255)
                logger.debug("Outdoor temp (0.1F)        : "+str(int(codecs.decode(packet[10:14], 'UTF-8'), 16))) # Outdoor Temp (0.1 deg F)
                logger.debug("Rain (0.1in)               : "+str(int(codecs.decode(packet[14:18], 'UTF-8'), 16))) # Rain* Long Term Total (0.01 inches)
                logger.debug("Barometer (0.1mbar)        : "+str(int(codecs.decode(packet[18:22], 'UTF-8'), 16))) # Barometer (0.1 mbar)
                logger.debug("Indoor Temp                : "+str(round((int(codecs.decode(packet[22:26], 'UTF-8'), 16)/10-32)/1.8,2))) # Indoor Temp (deg F)
                logger.debug("Outdoor humidity (0.1%)    : "+str(int(codecs.decode(packet[26:30], 'UTF-8'), 16))) # Outdoor Humidity (0.1%)
                logger.debug("Indoor Humidity (0.1%)     : "+str(int(codecs.decode(packet[30:34], 'UTF-8'), 16))) # Indoor Humidity (0.1%)
                logger.debug("Date (day of year)         : "+str(int(codecs.decode(packet[34:38], 'UTF-8'), 16))) # Date (day of year)
                logger.debug("Time (minute of day)       : "+str(int(codecs.decode(packet[38:42], 'UTF-8'), 16))) # Time (minute of day)
                logger.debug("Today's Rain Total (0.01in): "+str(int(codecs.decode(packet[42:46], 'UTF-8'), 16))) # Today's Rain Total (0.01 inches)*
                logger.debug("1Min Wind SPeed Average    : "+str(int(codecs.decode(packet[46:50], 'UTF-8'), 16))) # 1 Minute Wind Speed Average (0.1kph)*
                logger.debug("====================================")
                logger.debug(" ")
            
            # Wind Speed Calculations
            wind_speed = int(codecs.decode(packet[2:6], 'UTF-8'), 16)
            wind_speed = (wind_speed / 10)
            wind_speed = (wind_speed / 1.609344)
            wind_speed = round(wind_speed , 1)
            wx_wind_speed = wind_speed
            
            # Average Wind Speed Calculations
            average_wind_speed = int(codecs.decode(packet[46:50], 'UTF-8'), 16)
            average_wind_speed = (average_wind_speed / 10)
            average_wind_speed = (average_wind_speed / 1.609344)
            average_wind_speed = round(average_wind_speed , 1)
            wx_average_wind_speed = average_wind_speed
        
            # Wind Bearing Calculations
            x = int(codecs.decode(packet[6:10], 'UTF-8'), 16)
            y = ((int(x) / 255.0) * 360)
            wind_bearing = round(y)
            wx_wind_bearing = wind_bearing
            y = None
        
            # Wind Direction Calculations
            compass_brackets = ["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N"]
            compass_lookup = round(wind_bearing / 45)
            wind_direction = compass_brackets[compass_lookup]
            wx_wind_heading = wind_direction
        
            # Barometer Calculations
            barometer = int(codecs.decode(packet[18:22], 'UTF-8'), 16)
            barometer_mbar = (barometer / 10)
            barometer_inhg = (barometer_mbar / 33.8639)
            barometer_inhg = round(barometer_inhg, 2)
            wx_barometer = barometer_inhg
        
            # Temperature Calculations
            temperature = int(codecs.decode(packet[22:26], 'UTF-8'), 16)
            temperature = (temperature / 10)
            wx_temperature = temperature
            wx_temperature_celsius = round((wx_temperature - 32) / 1.8, 2)
        
            # Humidity Calculations
            humidity = int(codecs.decode(packet[26:30], 'UTF-8'), 16)
            humidity = (humidity / 10)
            wx_humidity = humidity
            
            # Total Rain Calculations
            total_rain = int(codecs.decode(packet[14:18], 'UTF-8'), 16)
            total_rain = (total_rain / 100)
            wx_total_rain = total_rain
            wx_total_rain_mm = total_rain / 24.5
        
            # Today Rain Calculations
            today_rain = int(codecs.decode(packet[42:46], 'UTF-8'), 16)
            today_rain = (today_rain / 100)
            wx_today_rain = today_rain
            wx_today_rain_mm = today_rain / 24.5
                
            # Determine whether we should open dome
            if (wx_average_wind_speed > float(self.config.get("MAXAVWIND"))) or (wx_wind_speed > float(self.config.get("MAXWIND"))):
                logger.info("Weather data is wind average "+str(wx_average_wind_speed)+" max is "+
                    self.config.get("MAXAVWIND")+"wind speed ",str(wx_wind_speed)+" max is ",
                    self.config.get("MAXWIND")+" returning True (weather not ok)")
                return True
            else:
                logger.info("Weather data is wind average "+str(wx_average_wind_speed)+" max is "+self.config.get("MAXAVWIND")+"wind speed "
                            +str(wx_wind_speed)+" max is "+self.config.get("MAXWIND")+" returning False (weather ok)")
                return False
        else:
            logging.warning("No data received from weather station")
            return True
        
