# -*- coding: utf-8 -*-
"""
Django settings.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys
from os.path import join, dirname

from configurations import Configuration, values

# fix `UUID is not JSON serializable django` bug
from json import JSONEncoder
from uuid import UUID
JSONEncoder_olddefault = JSONEncoder.default


def JSONEncoder_newdefault(self, o):
    if isinstance(o, UUID):
        return str(o)
    return JSONEncoder_olddefault(self, o)
JSONEncoder.default = JSONEncoder_newdefault


class Common(Configuration):
    reload(sys)
    sys.setdefaultencoding('utf-8')

    # COMMON CONFIGURATION
    BASE_DIR = dirname(dirname(__file__))
    PROJECT_NAME = 'wheat'
    ROOT_URLCONF = 'urls'
    API_URL = 'http://api.maili.cn'
    WEB_URL = 'http://maili.cn'
    API_VERSION = '0.1'
    # See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
    WSGI_APPLICATION = 'wsgi.application'
    # END COMMON CONFIGURATION

    # Custom user app defaults
    # Select the correct user model
    AUTH_USER_MODEL = "user.User"
    # LOGIN_REDIRECT_URL = "test_users:redirect"
    # LOGIN_URL = "account_login"
    # END Custom user app defaults

    # APP CONFIGURATION
    DJANGO_APPS = (
        # Default Django apps:
        'django.contrib.auth',
        'django.contrib.contenttypes',
        # 'django.contrib.sessions',
        # 'django.contrib.sites',
        # 'django.contrib.messages',
        'django.contrib.staticfiles',

        # Useful template tags:
        # 'django.contrib.humanize',

        # Admin
        # 'grappelli',
        'django.contrib.admin',
    )
    THIRD_PARTY_APPS = (
        # 'crispy_forms',  # Form layouts
        'cacheops',
        # 'django_extensions',
        'rest_framework',
        'rest_framework_swagger',
        # 'django_rq',
        'imagekit',
        # 'django_gravatar',
        # 'rest_framework_mongoengine',
        # 'haystack',
    )
    # Apps specific for this project go here.
    LOCAL_APPS = (
        # Your stuff: custom apps go here
        'apps.user',
        'apps.group',
        'apps.message',
        'apps.moment',
        'apps.image',
        'apps.pubsub',
        'apps.book',
        'apps.order',
    )
    # END LOCAL APPS

    # APP CONFIGURATION
    # See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
    INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS
    # END APP CONFIGURATION

    # REST FRAMEWORK CONFIGURATION
    AUTHTOKEN_EXPIRED_DAYS = 7 * 2
    REST_FRAMEWORK = {
        'PAGE_SIZE': 10,
        'PAGINATE_BY': 10,
        'DEFAULT_AUTHENTICATION_CLASSES': (
            # 'rest_framework.authentication.TokenAuthentication',
            'customs.authentications.XTokenAuthentication',
            # 'rest_framework.authentication.SessionAuthentication',
        ),
        'DEFAULT_PERMISSION_CLASSES': (
            'rest_framework.permissions.IsAuthenticated',
        ),
        'DEFAULT_RENDERER_CLASSES': (
            # 'customs.renderers.XJSONRenderer',
            'rest_framework.renderers.JSONRenderer',
            # 'customs.renderers.XAdminRenderer',
            'rest_framework.renderers.BrowsableAPIRenderer',

        ),
        # 'DEFAULT_CONTENT_NEGOTIATION_CLASS': 'customs.negotiation.XDefaultContentNegotiation',
        'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    }
    # END REST FRAMEWORK CONFIGURATION

    # SWAGGER CONFIGURATION
    # https://github.com/swagger-api/swagger-spec/blob/master/versions/1.2.md
    SWAGGER_SETTINGS = {
        "exclude_namespaces": [],
        "api_version": API_VERSION,
        "api_path": "/",
        "enabled_methods": [
            'get',
            'post',
            'put',
            'patch',
            'delete'
        ],
        "api_key": '80a93e3c435775c0dec28f6a2ebafa49',
        "is_authenticated": True,
        "is_superuser": False,
        # "permission_denied_handler": 'TODO',
        "info": {
            'contact': 'cyb@xinshu.me',
            'description': 'API documents',
            'title': 'API documents',
        },
    }
    # END SWAGGER CONFIGURATION

    # REDIS SESSION CONFIGURATION
    SESSION_ENGINE = 'redis_sessions.session'
    SESSION_REDIS_HOST = 'localhost'
    SESSION_REDIS_PORT = 6379
    SESSION_REDIS_DB = 0
    # SESSION_REDIS_PASSWORD = '123456'
    SESSION_REDIS_PREFIX = 'session'
    # END REDIS SESSION CONFIGURATION

    # RQ CONFIGURATION
    RQ_QUEUES = {
        'default': {
            'HOST': 'localhost',
            'PORT': 6379,
            'DB': 1,
            'DEFAULT_TIMEOUT': 900,
        },
        'high': {
            'HOST': 'localhost',
            'PORT': 6379,
            'DB': 1,
            'DEFAULT_TIMEOUT': 900,
        },
        'low': {
            'HOST': 'localhost',
            'PORT': 6379,
            'DB': 1,
            'DEFAULT_TIMEOUT': 900,
        },
    }
    # END RQ CONFIGURATION

    # CACHE OPS CONFIGURATION
    CACHEOPS_REDIS = {
        'host': 'localhost',  # redis-server is on same machine
        'port': 6379,        # default redis port
        'db': 2,             # SELECT non-default redis database
                             # using separate redis db or redis instance
                             # is highly recommended
        'socket_timeout': 3,
    }
    DEFAULT_CACHE_TIMEOUT = 60 * 30
    CACHE_QUERY = True  # CACHE DB QUERY
    CACHEOPS = {
        # Automatically cache any User.objects.get() calls for 15 minutes
        # This includes request.user or post.author access,
        # where Post.author is a foreign key to auth.User
        'auth.user': {'ops': 'get', 'timeout': 60 * 15},
        # 'apps.user.a': {'ops': 'get', 'timeout': 60 * 15},

        # Automatically cache all gets and queryset fetches
        # to other django.contrib.auth models for an hour
        'auth.*': {'ops': ('fetch', 'get'), 'timeout': 60 * 60},

        # Cache gets, fetches, counts and exists to Permission
        # 'all' is just an alias for ('get', 'fetch', 'count', 'exists')
        'auth.permission': {'ops': 'all', 'timeout': 60 * 60},

        # Enable manual caching on all other models with default timeout of an hour
        # Use Post.objects.cache().get(...)
        #  or Tags.objects.filter(...).order_by(...).cache()
        # to cache particular ORM request.
        # Invalidation is still automatic
        '*.*': {'ops': (), 'timeout': 60 * 60},

        # And since ops is empty by default you can rewrite last line as:
        '*.*': {'timeout': 60 * 60},
    }
    # END CACHE OPS CONFIGURATION

    # HAYSTACK CONFIGURATION
    HAYSTACK_CONNECTIONS = {
        # 'default': {
        #     'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        #     'URL': 'http://127.0.0.1:8983/solr'
        # ...or for multicore...
        # 'URL': 'http://127.0.0.1:8983/solr/mysite',
        # },
        'default': {
            'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
            'URL': 'http://127.0.0.1:9200/',
            'INDEX_NAME': 'haystack',
            'INCLUDE_SPELLING': True,
        }
    }
    # HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'
    HAYSTACK_SIGNAL_PROCESSOR = 'apps.search.signals.DelaySignalProcessor'
    HAYSTACK_SEARCH_RESULTS_PER_PAGE = 20
    HAYSTACK_SIGNAL_TRIGGER_MODELS = (
        # 'apps.article.models.Article',
    )
    # END HAYSTACK CONFIGURATION

    # CORS HEADER
    CORS_ALLOW_METHODS = (
        'GET',
        'POST',
        'PUT',
        'PATCH',
        'DELETE',
        'OPTIONS'
    )
    CORS_ALLOW_HEADERS = (
        'x-requested-with',
        'content-type',
        'accept',
        'origin',
        'authorization',
        'x-csrftoken',
        'X-CSRFToken'
    )
    CORS_PREFLIGHT_MAX_AGE = 86400
    CORS_ALLOW_CREDENTIALS = True
    CORS_REPLACE_HTTPS_REFERER = False
    # END CORS HEADER

    # EMAIL CONFIGURATION
    EMAIL_USE_TLS = False
    EMAIL_HOST = 'smtp.exmail.qq.com'
    EMAIL_PORT = 25
    EMAIL_HOST_USER = 'noreply@example.com'
    EMAIL_HOST_PASSWORD = '123456'
    # END EMAIL CONFIGURATION

    # LOGGING CONFIGURATION
    # See: https://docs.djangoproject.com/en/dev/ref/settings/#logging
    # A sample logging configuration. The only tangible logging
    # performed by this configuration is to send an email to
    # the site admins on every HTTP 500 error when DEBUG=False.
    # See http://docs.djangoproject.com/en/dev/topics/logging for
    # more details on how to customize your logging configuration.
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
        },
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse'
            }
        },
        'handlers': {
            'null': {
                'level': 'DEBUG',
                'class': 'logging.NullHandler',
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            },
            'mail_admins': {
                'level': 'ERROR',
                'filters': ['require_debug_false'],
                'class': 'django.utils.log.AdminEmailHandler',
                'include_html': True,
            },
            'error': {
                'level': 'ERROR',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(BASE_DIR, 'logs/error.log'),
                'maxBytes': '16777216',  # 16megabytes
                'formatter': 'verbose'
            },
            'query': {
                'level': 'ERROR',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(BASE_DIR, 'logs/query.log'),
                'maxBytes': '16777216',  # 16megabytes
                'formatter': 'verbose'
            },
            'pubsub': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(BASE_DIR, 'logs/redis-pubsub-supervisor.log'),
                'maxBytes': '16777216',  # 16megabytes
                'formatter': 'verbose'
            },
            'order': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(BASE_DIR, 'logs/order.log'),
                'maxBytes': '16777216',  # 16megabytes
                'formatter': 'verbose'
            },
        },
        'loggers': {
            'django.request': {
                'handlers': ['mail_admins'],
                'level': 'ERROR',
                'propagate': True,
            },
            'django': {
                'handlers': ['error', 'query'],
                'level': 'ERROR',
                'propagate': True,
            },
            'pubsub': {
                'handlers': ['pubsub'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'order': {
                'handlers': ['order'],
                'level': 'DEBUG',
                'propagate': True,
            },
        },
        # you can also shortcut 'loggers' and just configure logging for EVERYTHING at once
        'root': {
            'handlers': ['console', 'mail_admins'],
            'level': 'INFO'
        },
    }
    # END LOGGING CONFIGURATION

    # MIDDLEWARE CONFIGURATION
    MIDDLEWARE_CLASSES = (
        # 'django.middleware.cache.UpdateCacheMiddleware',    # This must be first on the list
        # Make sure djangosecure.middleware.SecurityMiddleware is listed first
        'djangosecure.middleware.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'corsheaders.middleware.CorsMiddleware',
        'django.middleware.common.CommonMiddleware',

        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        # 'django.middleware.cache.FetchFromCacheMiddleware',  # This must be last
    )
    # END MIDDLEWARE CONFIGURATION

    # MIGRATIONS CONFIGURATION
    # MIGRATION_MODULES = {
    #     'sites': 'contrib.sites.migrations'
    # }
    # END MIGRATIONS CONFIGURATION

    # DEBUG
    # See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
    DEBUG = values.BooleanValue(False)
    # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
    TEMPLATE_DEBUG = DEBUG
    # END DEBUG

    # SECRET CONFIGURATION
    # See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
    # Note: This key only used for development and testing.
    #       In production, this is changed to a values.SecretValue() setting
    SECRET_KEY = "r2=_vzt7(8dcl+yyo*4dmef&jp&iwxb=6*4f59r)h^0udgtwb1"
    # END SECRET CONFIGURATION

    # FIXTURE CONFIGURATION
    # See:
    # https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-FIXTURE_DIRS
    FIXTURE_DIRS = (
        join(BASE_DIR, 'fixtures'),
    )
    # END FIXTURE CONFIGURATION

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
            'PASSWORD': '',                  # Not used with sqlite3.
            # Set to empty string for localhost. Not used with sqlite3.
            'HOST': '127.0.0.1',
            # Set to empty string for default. Not used with sqlite3.
            'ili$20!6PORT': '3306',
            # 'TEST_CHARSET': 'utf8',
            # 'TEST_COLLATION': 'utf8_general_ci',
            'OPTIONS': {'charset': 'utf8mb4'},
        },
    }
    # END DATABASE CONFIGURATION

    # CACHING
    # Do this here because thanks to django-pylibmc-sasl and pylibmc
    # memcacheify (used on heroku) is painful to install on windows.
    # CACHES = {
    #     'default': {
    #         'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    #         'LOCATION': ''
    #     }
    # }
    # END CACHING

    # GENERAL CONFIGURATION
    # See: https://docs.djangoproject.com/en/dev/ref/settings/#time-zone
    TIME_ZONE = 'Asia/Shanghai'

    # See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
    LANGUAGE_CODE = 'en-us'

    # See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
    SITE_ID = 1

    # See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
    USE_I18N = True

    # See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
    USE_L10N = True

    # See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
    USE_TZ = False
    # END GENERAL CONFIGURATION

    # TEMPLATE CONFIGURATION
    # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
    TEMPLATE_CONTEXT_PROCESSORS = (
        'django.contrib.auth.context_processors.auth',
        'django.core.context_processors.debug',
        'django.core.context_processors.i18n',
        'django.core.context_processors.media',
        'django.core.context_processors.static',
        'django.core.context_processors.tz',
        'django.contrib.messages.context_processors.messages',
        'django.core.context_processors.request',
        # Your stuff: custom template context processers go here
    )
    # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
    TEMPLATE_DIRS = (
        join(BASE_DIR, 'templates'),
    )
    TEMPLATE_LOADERS = (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )
    # See: http://django-crispy-forms.readthedocs.org/en/latest/install.html#template-packs
    CRISPY_TEMPLATE_PACK = 'bootstrap3'
    # END TEMPLATE CONFIGURATION

    # STATIC FILE CONFIGURATION
    # See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
    STATIC_ROOT = join(BASE_DIR, 'static')

    # See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
    STATIC_URL = '/static/'

    # See:
    # https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
    # STATICFILES_DIRS = (
    #    join(BASE_DIR, 'static'),
    # )

    # See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
    STATICFILES_FINDERS = (
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    )
    # END STATIC FILE CONFIGURATION

    # MEDIA CONFIGURATION
    # See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
    MEDIA_ROOT = join(BASE_DIR, 'media')
    # See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
    BASE_URL = ''
    MEDIA_URL = '/media/'
    # END MEDIA CONFIGURATION

    # AUTHENTICATION CONFIGURATION
    AUTHENTICATION_BACKENDS = (
        "django.contrib.auth.backends.ModelBackend",
    )
    # Some really nice defaults
    ACCOUNT_AUTHENTICATION_METHOD = "username"
    ACCOUNT_EMAIL_REQUIRED = True
    ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    # END AUTHENTICATION CONFIGURATION

    # SLUGLIFIER
    # AUTOSLUG_SLUGIFY_FUNCTION = "slugify.slugify"
    # END SLUGLIFIER

    # REDIS DB
    REDIS_PUBSUB_DB = 2
    REDIS_PUBSUB_TAG = 'dev'
    REDIS_PUBSUB_CHANNEL = 'as12afzxjk@askfl'
    # END REDIS DB

    if 'test' in sys.argv:
        DATABASES['default'] = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'mydatabase'
        }
