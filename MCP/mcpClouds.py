import sys
import argparse
from pathlib import Path
import time
from datetime import datetime
from datetime import timedelta
import numpy
import cv2
import PIL
from PIL import Image
import logging
import sqlite3
import keras

from mcpConfig import McpConfig
config=McpConfig()

sys.path.append(str(Path(__file__).parent.absolute().parent))

logger = logging.getLogger("oMCP")

KERAS_MODEL = 'keras_model.h5'

# derived from indi-allsky by Aaron Morris https://github.com/aaronwmorris/indi-allsky.git thanks Aaron!

class McpClouds(object):
    CLASS_NAMES = (
        'Clear',
        'Cloudy',
    )
    
    def __init__(self):
        self.config = config

    def isCloudy(self):
        logger.warning('Using keras model: %s', KERAS_MODEL)
        self.model = keras.models.load_model(KERAS_MODEL)

        image_file = config.get("ALLSKY_IMAGE")
        logger.info('Loading image: %s', image_file)

        ### PIL
        try:
            with Image.open(str(image_file)) as img:
                image_data = cv2.cvtColor(numpy.array(img), cv2.COLOR_RGB2BGR)
        except PIL.UnidentifiedImageError:
            logger.error('Invalid image file: %s', image_file)
            return True

        return (self.detect(image_data) != 'Clear')

    def detect(self, image):
        thumbnail = cv2.resize(image, (224, 224))
        normalized_thumbnail = (thumbnail.astype(numpy.float32) / 127.5) - 1
        data = numpy.ndarray(shape=(1, 224, 224, 3), dtype=numpy.float32)
        data[0] = normalized_thumbnail
        detect_start = time.time()

        # Predicts the model
        prediction = self.model.predict(data)
        idx = numpy.argmax(prediction)
        class_name = self.CLASS_NAMES[idx]
        confidence_score = (prediction[0][idx]).astype(numpy.float32)

        detect_elapsed_s = time.time() - detect_start
        logger.info('Cloud detection in %0.4f s', detect_elapsed_s)
        logger.info('Rating: %s, Confidence %0.3f', class_name, confidence_score)
        
        return(class_name)

