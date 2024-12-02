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

ALLOWED_HOSTS = ['spao-master.local','localhost','127.0.0.1']

# Application definition
INSTALLED_APPS = [
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
    # Local
    "pages.apps.PagesConfig",
    "accounts.apps.AccountsConfig",
    "setup.apps.SetupConfig",
    "targets.apps.TargetsConfig",
    "observations.apps.ObservationsConfig",
    "operations.apps.OperationsConfig",
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
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

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = "accounts.CustomUser"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
MEDIA_URL = "/media/" 
MEDIA_ROOT = BASE_DIR / "media" 

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
## Configuration should be migrated to the config object                                 ##
###########################################################################################
# Read the private.ini file for settings that should not be in the public settings.py file
from obsy.config import Config
config = Config()

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

###########################################################################################
## Task Scheduling and Integration                                                       ##
###########################################################################################
# Celery Configuration Options
from celery.schedules import crontab
BROKER_URL = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/')
CELERY_BROKER_URL = 'amqp://localhost'
CELERY_RESULT_BACKEND = 'rpc://'
CELERY_BEAT_SCHEDULE = {
    'daily-observations-task': {
        'task': 'observations.tasks.daily_observations_task',
        'schedule': crontab(hour=10, minute=0),
    },
}

###########################################################################################
## Application Settings                                                                  ##
###########################################################################################
# Settings for the postProcess module
SOURCEPATH="/home/gtulloch/obsy/sample_data/Processing/input"
REPOPATH="/home/gtulloch/obsy/sample_data/Processing/repo/"