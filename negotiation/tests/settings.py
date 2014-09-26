# coding=utf-8

SECRET_KEY = 'blabla'

DEBUG = True

SITE_ID = 1

# Installed Apps configuration

DEFAULT_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
)

THIRD_PARTY_APPS = (
    'permissions',
    'workflows',
    'business_workflow',
)

LOCAL_APPS = (
    'negotiation',
    'negotiation.tests'
)


INSTALLED_APPS = DEFAULT_APPS + THIRD_PARTY_APPS + LOCAL_APPS

ROOT_URLCONF = 'negotiation.tests.urls'

USE_I18N = True

USE_L10N = True

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}