import ephem

# Create an observer
observer = ephem.Observer()
observer.date = ephem.Date('2024/05/30')  # Set your specific date and time

# Set the location (e.g., Fredericton, Canada)
observer.lon = str(-66.666667)  # Longitude in string format
observer.lat = str(45.95)       # Latitude in string format
observer.elev = 20              # Elevation in meters

# Set the horizon for astronomical twilight (-18 degrees)
observer.horizon = "-18"

# Calculate the end of astronomical twilight
end_astronomical_twilight = observer.next_setting(ephem.Sun(), use_center=True)
print(type(end_astronomical_twilight ))
print("End of astronomical twilight:", end_astronomical_twilight)