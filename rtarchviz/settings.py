"""
Django settings for rtarchviz project.

Generated by 'django-admin startproject' using Django 1.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import dj_database_url
# import environmental variables set locally
if os.path.exists('env.py'):
    import env

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

ALLOWED_HOSTS = ['rtarchviz.herokuapp.com', 'localhost']

# Use custom User class for accounts
AUTH_USER_MODEL = 'accounts.User'
# Use custom Authentication Backends
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'accounts.backends.EmailAuth',
)

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'pages',
    'accounts',
    'blog',
    'bootstrap4',
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

ROOT_URLCONF = 'rtarchviz.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # add context processors for media files
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'rtarchviz.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-uk'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
STATIC_URL = '/static/'
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"), )
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files (images)
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Log DEBUG information to the console
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'console': {
#             'class': 'logging.StreamHandler',
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['console'],
#             'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
#         },
#     },
# }

try:
    if os.environ["ENV"] == 'development':
        '''
        DEVELOPMENT environment
        settings
        '''
        print "***You are in development mode"

        # Turn on django debug mode
        print "***debug mode is ON"
        DEBUG = True

        # Add debug toolbar
        print "***Debug Toolbar is ON"
        INSTALLED_APPS.append('debug_toolbar')
        MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')
        INTERNAL_IPS = ('127.0.0.1',)

        if "DATABASE_URL" in os.environ:
            # Use for testing using production db
            print "***Using production PostgreSQL dtabase providion on Heroku for development"
            DATABASES = {
                'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
            }
        else:
            # using the default local sqlite db
            print "***Using Django's local sqlite db for development"
            DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
                }
        }

    elif os.environ["ENV"] == 'production':
        ''' 
        PRODUCTION environment
        settings
        '''

        DEBUG = False

        # Add whitenoise for deploying app with static files to Heroku 
        MIDDLEWARE.append('whitenoise.middleware.WhiteNoiseMiddleware')

        # Use production Postgres database provisioned on Heroku
        if "DATABASE_URL" in os.environ:
            DATABASES = {
            'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
        }
        else:
            print "***no production database found. Provision one in Heroku and link to it using env variable 'DATABASE_URL'"

except KeyError:
    print "***ENV variable not set. Please set the environment variable 'ENV' to 'development' or 'production'"

# Settings for User Password Recovery
if "EMAIL_HOST_USER" and "EMAIL_HOST_PASSWORD" in os.environ:
    # Email setup for sending password recovery emails to users from a gmail account
    EMAIL_USE_TLS = True
    EMAIL_HOST = 'smtp.gmail.com' # need to 'Allow less secure apps' in gmail account settings
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER') # email address
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD') # password
    EMAIL_PORT = 587
else:
    # Print password reset email to the console
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'