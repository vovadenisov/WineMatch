# coding=utf-8
"""
Django settings for application project.

Generated by 'django-admin startproject' using Django 1.10.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
import configparser

SOURCE_ROOT = (os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + '/'
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!


# SECURITY WARNING: don't run with debug turned on in production!


PROJECT_NAME = 'WineMatch'

local_config_path = os.path.join(
    PROJECT_ROOT, 'conf', '{0}.conf'.format(PROJECT_NAME)
)

config = configparser.ConfigParser()

if os.path.exists(local_config_path):
    config.read(local_config_path)
else:
    raise Exception("Разместите конфиг файл проекта в папке conf на уровень выше проекта")

SECRET_KEY = config.get('secret', 'KEY')

debug_key = config.get("debug", "DEBUG")

if debug_key == "TRUE":
    DEBUG = True
else:
    DEBUG = False


# Application definition

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "78.155.218.63", "winematch.ru", "winematch"]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

CREATED_APPS = [
    'users',
    'survey',
    'wine',
    'feedback'
]

INSTALLED_APPS += CREATED_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'users.all_authenticate.authenticate_middleware'
]

ROOT_URLCONF = 'application.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [SOURCE_ROOT + 'Templates/'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'application.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

TARANTOOL_URL = config.get('tarantool', 'URL')
TARANTOOL_PORT = config.get('tarantool', 'PORT')
TARANTOOL_USER = config.get('tarantool', 'USER')
TARANTOOL_PASSWORD = config.get('tarantool', 'PASSWORD')

DATABASES = {
    'default': {
        'ENGINE': config.get('database_default', 'DATABASE_BACKEND'),
        'NAME': config.get('database_default', 'DATABASE_NAME'),
        'TEST': {
            'ENGINE': 'django.db.backends.sqlite3',
        },
        'USER': config.get('database_default', 'DATABASE_USER'),
        'PASSWORD': config.get('database_default', 'DATABASE_PASSWORD'),
        'HOST': config.get('database_default', 'DATABASE_HOST'),
        'PORT': config.get('database_default', 'DATABASE_PORT'),
        'OPTIONS': {'charset': 'utf8'},
        'CONN_MAX_AGE': 0
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
MEDIA_URL = '/media/'
MEDIA_ROOT = config.get('media', 'MEDIA_ROOT')
STATICFILES_DIRS = os.path.join(SOURCE_ROOT, "static"),
STATIC_ROOT = config.get('static', 'STATIC_DIR')

AUTH_USER_MODEL = "users.UserModel"

SESSION_SAVE_EVERY_REQUEST = True

SESSION_COOKIE_AGE = 12096000

MATCH_URL = config.get('match_system', 'BASE_URL')

ADMINS = (
    ('Vladimir Denisov', 'v.denisov@corp.mail.ru'),
    ('Anastasiya Dudina', 'a.dyudina@corp.mail.ru'),
)

EMAIL_HOST = config.get('mailing', 'EMAIL_HOST')
EMAIL_PORT = config.get('mailing', 'EMAIL_PORT')
EMAIL_HOST_USER = config.get('mailing', 'EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config.get('mailing', 'EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
SERVER_EMAIL = EMAIL_HOST_USER
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_USE_SSL=True
