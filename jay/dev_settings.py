import os

from jay.settings import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '$ji7r1i0&rcpuovz7e@4@)shpt6#@z$i!rt7ual42+d-o8ei(5'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SQlite for dev will do

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}
