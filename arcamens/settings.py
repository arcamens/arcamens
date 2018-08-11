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
# In days.
SIGNUP_EXP = 2

ONE_SIGNAL_APPID = 'e4387e31-b5c1-493a-8a28-f56bfed98c27'
ONE_SIGNAL_API_KEY = 'YjQ5NDc3MWItYzNjNS00MmZhLWEyNTYtZTk5YjJkYjkwZTY4'
ONE_SIGNAL_DEVICE_APP = 'core_app'
ONE_SIGNAL_DEVICE_MODEL = 'User'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAYMENTS_REALM = 'arcamens123'
PAYPAL_ID = 'CDA2QQH9TQ44C' #PayPal account ID` to `arcamens/settings.py`

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '9!3k4j3p94v4jl!2ex^(ep$y7-^e4is9a!d-xw)pj$unf(o@m7'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1']

# The addon bots settings.
ARCAMENS_BOT_EMAIL = 'arcabot@arcamens.com'
ARCAMENS_BOT_NAME = 'Arcamens Service'

BITBUCKET_BOT_EMAIL = 'bitbot@arcamens.com'
BITBUCKET_BOT_NAME = 'Bitbucket Service'

GITHUB_BOT_EMAIL = 'hubbot@arcamens.com'
GITHUB_BOT_NAME = 'Github Service'

# When the user is not authenticated it is redirected by slock AuthenticatedView.
AUTH_ERR = 'core_app/unauthorized.html'
DEFAULT_ERR = 'core_app/default-error.html'
LOGOUT_VIEW = 'site_app:logged-out'
LOGGED_VIEW = 'core_app:index'

PAYBILLS_USER = 'core_app.User'

CURRENCY_CODE = 'USD'
PAYPAL_URL = 'https://www.sandbox.paypal.com'
PAYPAL_IPN_DOMAIN = 'https://staging.arcamens.com'
PAYPAL_IPN_VIEW   = 'cash_app:paypal-ipn'
PAYPAL_BUSINESS_NAME = ''

# Max users per account for free plan.
FREE_MAX_USERS = 3
USER_COST      = 10

# Mail settings.

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'arcamens.softwares@gmail.com'
EMAIL_HOST_PASSWORD = 'arcamenssoftwares'

# just a workaround.
LOCAL_ADDR = 'http://127.0.0.1:8000'

NOCAPTCHA = True

# For debugging on 0.0.0.0.
RECAPTCHA_PUBLIC_KEY = '6LfqPWkUAAAAAHygjNgWFhU3KvssnSWWTzAgT2kl'
RECAPTCHA_PRIVATE_KEY = '6LfqPWkUAAAAANS1MGLmRN4H5_yTAIQ7oaAOOpYK'

FREE_STORAGE_LIMIT = 1 * 1024 * 1024
PAID_STORAGE_LIMIT = 2 * 1024 * 1024

FREE_DOWNLOAD_LIMIT = 2 * 1024 * 1024
PAID_DOWNLOAD_LIMIT = 2 * 1024 * 1024

FREE_MAX_FILE_SIZE = 1000 * 1024 * 1024
PAID_MAX_FILE_SIZE = 1 * 1024 * 1024

# Production.
# RECAPTCHA_PUBLIC_KEY = '6Lfz3lUUAAAAAJh0h0dNMWqgx-rGZR_aY9FJRecP'
# RECAPTCHA_PRIVATE_KEY = '6Lfz3lUUAAAAAEdgDWRrN2yLPVDR1pyNhW_6UPil'

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
    'group_app',
    'post_app',
    'comment_app',
    'paybills',
    'board_app',
    'site_app', 
    'cash_app',
    'datetimewidget',
    'list_app', 
    'card_app', 
    'jsim',
    'jscroll',
    'snippet_app',
    'note_app',
    'bootstrap3',
    'blowdb',
    'slock',
    'onesignal',
    'listutils',
    'captcha',
    'bitbucket_app',
    'github_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core_app.middleware.FixTimezone',

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




























