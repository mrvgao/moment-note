# -*- coding: utf-8 -*-
'''
Local Configurations

- Runs in Debug mode
- Uses console backend for emails
- Use Django Debug Toolbar
'''
from configurations import values
from .common import Common


class Local(Common):

    SECRET_KEY = "r2=_vzt7(8dcl+yyo*4dmef&jp&iwxb=6*4f59r)h^0udgtwb1"

    # DEBUG
    DEBUG = values.BooleanValue(True)
    TEMPLATE_DEBUG = DEBUG
    # END DEBUG

    ALLOWED_HOSTS = ['121.40.158.110']

    # INSTALLED_APPS
    INSTALLED_APPS = Common.INSTALLED_APPS
    # END INSTALLED_APPS

    # django-debug-toolbar
    # MIDDLEWARE_CLASSES = Common.MIDDLEWARE_CLASSES + ('debug_toolbar.middleware.DebugToolbarMiddleware',)
    # INSTALLED_APPS += ('debug_toolbar',)

    # INTERNAL_IPS = ('127.0.0.1',)

    # DEBUG_TOOLBAR_CONFIG = {
    #     'DISABLE_PANELS': [
    #         'debug_toolbar.panels.redirects.RedirectsPanel',
    #     ],
    #     'SHOW_TEMPLATE_CONTEXT': True,
    # }
    # end django-debug-toolbar

    CACHE_QUERY = False  # CACHE DB QUERY
    # DATABASE CONFIGURATION
    # See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
    DATABASES = {
        'default': {
            # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or
            # 'oracle'.
            'ENGINE': 'django.db.backends.mysql',
            # Or path to database file if using sqlite3.
            'NAME': 'wheat',
            'USER': 'root',                      # Not used with sqlite3.
            'PASSWORD': 'Maili$20!6',                  # Not used with sqlite3.
            # Set to empty string for localhost. Not used with sqlite3.
            'HOST': '127.0.0.1',
            # Set to empty string for default. Not used with sqlite3.
            'PORT': '3306',
            # 'TEST_CHARSET': 'utf8',
            # 'TEST_COLLATION': 'utf8_general_ci',
            'OPTIONS': {'charset': 'utf8mb4'},
        },
    }
    # END DATABASE CONFIGURATION

    # REDIS DB
    REDIS_PUBSUB_DB = 2
    REDIS_PUBSUB_TAG = 'book'
    # END REDIS DB
