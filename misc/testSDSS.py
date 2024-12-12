import requests
from PIL import Image
from io import BytesIO

# Define the coordinates of the object (RA and Dec) and the desired image size
ra = 180.0  # Right Ascension
dec = 0.0   # Declination
scale = 0.2  # Scale (arcsec/pixel)
width = 100  # Width of the image in pixels
height = 100  # Height of the image in pixels

# Construct the URL for the SDSS SkyServer Image Cutout service
url = f"http://skyserver.sdss.org/dr16/SkyServerWS/ImgCutout/getjpeg?ra={ra}&dec={dec}&scale={scale}&width={width}&height={height}"

# Make the request to fetch the image
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Open the image using PIL
    image = Image.open(BytesIO(response.content))
    # Save the image to a file
    image.save("thumbnail.jpg")
    print("Image saved as thumbnail.jpg")
else:
    print("Failed to retrieve image")