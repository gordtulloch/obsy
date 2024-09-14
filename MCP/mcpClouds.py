import sys
import argparse
from pathlib import Path
import time
from datetime import datetime
from datetime import timedelta
import cv2
import PIL
from PIL import Image
import logging
import sqlite3
import keras
import os
import shutil
import numpy as np

from mcpConfig import McpConfig
config=McpConfig()

sys.path.append(str(Path(__file__).parent.absolute().parent))

logger = logging.getLogger("mcpClouds")

KERAS_MODEL = 'keras_model.h5'

# derived from indi-allsky by Aaron Morris https://github.com/aaronwmorris/indi-allsky.git thanks Aaron!

class McpClouds(object):
    CLASS_NAMES = (
        'Clear',
        'Cloudy',
    )
    
    def __init__(self):
        self.config = config
        modelFilename = os.path.join(os.path.dirname(os.path.realpath(__file__)), config.get("KERASMODEL"))
        logger.info('Using keras model: %s', modelFilename)
        self.model = keras.models.load_model(modelFilename, compile=False)
        self.imageCount=0
        # Set up the image paths if required
        if not os.path.exists(config.get("ALLSKYSAMPLEDIR")):
            os.makedirs(config.get("ALLSKYSAMPLEDIR"))
        for className in self.CLASS_NAMES:
            if not os.path.exists(config.get("ALLSKYSAMPLEDIR")+"/"+className):
                os.makedirs(config.get("ALLSKYSAMPLEDIR")+"/"+className)

    def isCloudy(self,allskysampling=False):
        if (self.config.get("ALLSKYCAM") == "NONE"):
            logger.error('No allsky camera for cloud detection')
        else:
            if (self.config.get("ALLSKYCAM") == "INDI-ALLSKY"):
                # Query the database for the latest file
                try:
                    conn = sqlite3.connect('/var/lib/indi-allsky/indi-allsky.sqlite')
                    cur = conn.cursor()
                    sqlStmt='SELECT image.filename AS image_filename FROM image ' + \
                    'JOIN camera ON camera.id = image.camera_id WHERE camera.id = '+ self.config.get("ALLSKYCAMNO") +\
                    ' ORDER BY image.createDate DESC LIMIT 1'
                    logger.debug('Running SQL Statement: '+sqlStmt)
                    cur.execute(sqlStmt)
                    image_file=cur.fetchone()
                    image_file='/var/www/html/allsky/images/'+image_file[0]
                    conn.close()
                except sqlite3.Error as e:
                    logger.error("SQLITE Error accessing indi-allsky "+str(e))
                    exit(0)
            else:
                # Grab the image file from whereever
                image_file = config.get("ALLSKY_IMAGE")

        logger.info('Loading image: %s', image_file)
        
        result=self.detect(image_file)
      
        logger.info("Sampling is "+str(allskysampling)+" after "+config.get("ALLSKYSAMPLERATE")+" iterations. Count="+str(self.imageCount))

        # If allskysampling turned on save a copy of the image if count = allskysamplerate
        if (self.imageCount==int(config.get("ALLSKYSAMPLERATE"))):
            logger.info('Archiving '+image_file+" to "+config.get("ALLSKYSAMPLEDIR")+"/"+result)
            shutil.copy(image_file, config.get("ALLSKYSAMPLEDIR")+"/"+result)
            self.imageCount=0
        else:
            self.imageCount+=1

        return (result != 'Clear',result)

    def detect(self, imagePath):
        # Load and preprocess the image
        image = Image.open(imagePath)
        image = image.resize((256, 256))
        image_array = np.array(image) / 255.0
        image_array = np.expand_dims(image_array, axis=0)
        detect_start = time.time()

        # Predicts the model
        prediction = self.model.predict(image_array)
        idx = np.argmax(prediction)
        class_name = self.CLASS_NAMES[idx]
        confidence_score = (prediction[0][idx]).astype(np.float32)

        detect_elapsed_s = time.time() - detect_start
        logger.info('Cloud detection in %0.4f s', detect_elapsed_s)
        logger.info('Rating: %s, Confidence %0.3f', class_name, confidence_score)
        
        return(class_name)

