###########################################################################################
## Django Settings File                                                                  ##
###########################################################################################
from pathlib import Path
import os
import logging
logger = logging.getLogger(__name__)

# Global Version Number
VERSION = '1.0.0'

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-m=ct8%jslv^q*-%o5y-zw7k_=5kc#h9_#khyq#a34y%85la9zv'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    "django_admin_dracula",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party
    "crispy_forms", 
    "crispy_bootstrap5", 
    'celery',    
    'django_celery_results',
    'django_celery_beat',
    # Local
    "pages.apps.PagesConfig",
    "accounts.apps.AccountsConfig",
    "setup.apps.SetupConfig",
    "targets.apps.TargetsConfig",
    "observations.apps.ObservationsConfig",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'obsy.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'obsy.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# Load environment variables from .env file if not running in Docker (i.e. dev environment) and use SQLite3
if not os.getenv('DOCKER_CONTAINER'):
    from dotenv import load_dotenv
    load_dotenv()
    
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DATABASE_NAME'),
            'USER': os.getenv('DATABASE_USER'),
            'PASSWORD': os.getenv('DATABASE_PASSWORD'),
            'HOST': os.getenv('DATABASE_HOST'),
            'PORT': os.getenv('DATABASE_PORT'),
        }
    }

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Winnipeg'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = "accounts.CustomUser"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"

# django-crispy-forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5" 
CRISPY_TEMPLATE_PACK = "bootstrap5" 

###########################################################################################
## Logging Configuration                                                                 ##
###########################################################################################
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level':'INFO',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': 'obsy.log',
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5,
            'formatter':'standard',
        },  
        'request_handler': {
                'level':'INFO',
                'class':'logging.handlers.RotatingFileHandler',
                'filename': 'obsy.log',
                'maxBytes': 1024*1024*5, # 5 MB
                'backupCount': 5,
                'formatter':'standard',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        },

        'observations': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        },
        'targets': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        },
        
        'setup': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        },
        'accounts': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        },
        'django.request': {
            'handlers': ['request_handler'],
            'level': 'WARNING',
            'propagate': False
        },
    }
}

###########################################################################################
## End user Configuration should be migrated to the config object                        ##
###########################################################################################
# Read the private.ini file for settings that should not be in the public settings.py file
# These should eventually be in the database with a UI for the user to change them
from obsy.config import Config
config = Config()

###########################################################################################
## Task Scheduling and Integration                                                       ##
###########################################################################################
# Celery Configuration Options
# Celery settings
CELERY_BROKER_URL = 'pyamqp://guest@rabbitmq//'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']  # Ignore other content
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_ENABLE_UTC = True

from celery.schedules import solar

CELERY_BEAT_SCHEDULE = {
    # Executes at local sunrise
    'daily-observations-task': {
        'task': 'observations.tasks.daily_observations_task',
        'schedule': solar('sunrise', float(config.get("LATITUDE")), float(config.get("LONGITUDE"))),
    },
}


###########################################################################################
## Notifications                                                                         ##
###########################################################################################
# Setup for email notifications
EMAIL_BACKEND           = config.get("EMAIL_BACKEND")
EMAIL_HOST              = config.get("EMAIL_HOST")
EMAIL_PORT              = config.get("EMAIL_PORT")
EMAIL_USE_TLS           = config.get("EMAIL_USE_TLS")
EMAIL_HOST_USER         = config.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD     = config.get("EMAIL_HOST_PASSWORD")
SENDER_EMAIL            = config.get("SENDER_EMAIL")
RECIPIENT_EMAIL         = config.get("RECIPIENT_EMAIL")
# Set up for Bluesky notifications

# Set up for Twlio notifications
TWILIO_SID              = config.get("TWILIO_SID")
TWILIO_TOKEN            = config.get("TWILIO_TOKEN")

###########################################################################################
## Application Settings                                                                  ##
###########################################################################################
# Settings for the postProcess module
SOURCEPATH=config.get("PPSOURCEPATH")
REPOPATH=config.get("PPREPOPATH")

LATITUDE=config.get("LATITUDE")
LONGITUDE=config.get("LONGITUDE")
ELEVATION=config.get("ELEVATION")