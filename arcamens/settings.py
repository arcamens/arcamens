"""
Django settings for arcamens project.

Generated by 'django-admin startproject' using Django 1.10.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
from paybills.misc import get_addr
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAYMENTS_REALM = 'arcamens123'
PAYPAL_ID = 'CDA2QQH9TQ44C' #PayPal account ID` to `arcamens/settings.py`

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '9!3k4j3p94v4jl!2ex^(ep$y7-^e4is9a!d-xw)pj$unf(o@m7'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['0.0.0.0']

# When the user is not authenticated it is redirected by slock AuthenticatedView.
AUTH_ERR = 'core_app/unauthorized.html'
DEFAULT_ERR = 'core_app/default-error.html'
LOGOUT_VIEW = 'site_app:logged-out'
LOGGED_VIEW = 'core_app:index'

PAYBILLS_USER = 'core_app.User'
# DEBUG_PAYPAL_IPN_DOMAIN = get_addr(8000)
DEBUG_PAYPAL_IPN_DOMAIN = '0.0.0.0:8000'

PAYPAL_IPN_DOMAIN = 'http://arcamens.arcamens.com'
PAYPAL_IPN_VIEW   = 'site_app:paypal-ipn'
PAYPAL_BUSINESS_NAME = ''

WS_HOST = '127.0.0.1'
WS_PORT = 15675
WS_USE_SSL = 'false'

# Mail settings.

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'arcamens.softwares@gmail.com'
EMAIL_HOST_PASSWORD = 'arcamenssoftwares'

# just a workaround.
LOCAL_ADDR = 'http://0.0.0.0:8000'if DEBUG else 'http://www.arcamens.com'

MQTT_HOST = "127.0.0.1"  
MQTT_USER = "guest"  
MQTT_PASS = "guest"  
MQTT_PORT = 1883

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # It has to be in this order otherwise we get
    # dependencies order issues?
    'core_app',
    'timeline_app',
    'post_app',
    'comment_app',
    'paybills',
    'board_app',
    'site_app', 
    'list_app', 
    'card_app', 
    'jsim',
    'snippet_app',
    'note_app',
    'bootstrap3',
    'blowdb',
    'slock',
    'wsbells',
    'bitbucket_app',
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

ROOT_URLCONF = 'arcamens.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'arcamens.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = (
     os.path.join('arcamens', 'static'),
 )

MEDIA_ROOT = os.path.join(BASE_DIR, 'arcamens', 'static/media')
MEDIA_URL ='/static/media/'

try:
    from local_settings import *
except ImportError:
    pass



















