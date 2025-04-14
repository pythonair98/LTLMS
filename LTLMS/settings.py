"""
Django settings for LTLMS project.

Generated by 'django-admin startproject' using Django 5.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from pathlib import Path
import pymysql

pymysql.install_as_MySQLdb()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

#
# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, "static"),
# ]
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-b5af10c63e**-73bnz^c*+rk5u%-9)!@#5uy5^#^*%r09rm7r1"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
CSRF_TRUSTED_ORIGINS = [
    'https://milahaarabia.com',
    "http://127.0.0.1",
    "http://localhost",
]

ALLOWED_HOSTS = ['*']

EMAIL_BACKEND = 'zoho_zeptomail.backend.zeptomail_backend.ZohoZeptoMailEmailBackend'
DEFAULT_FROM_EMAIL = 'info@milahaarabia.com'
ZOHO_ZEPTOMAIL_API_KEY_TOKEN = 'Zoho-enczapikey wSsVR60n+R/1XfgryWapJ+s/nV5QVF70RBwvjlP043L0HvDFp8c6kkefUAD0FfNMFDZgQTYarOggzRgG1WINitQpygoADCiF9mqRe1U4J3x17qnvhDzJXmlemxOMKo4BxQlonGJiEcEk+g=='
ZOHO_ZEPTOMAIL_HOSTED_REGION = 'zeptomail.zoho.com'

# Application definition
DATE_INPUT_FORMATS = ["%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%d-%b-%Y"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "user_auth.apps.UserAuthConfig",
    "ILAS.apps.LicesnsingConfig",
    "crispy_forms",
    "crispy_bootstrap5",
    "widget_tweaks",
    "reports.apps.ReportsConfig",
    "django_extensions",
    "django_seed",
]
USE_TZ = False


CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"
SECURE_CROSS_ORIGIN_OPENER_POLICY = None
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "LTLMS.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "LTLMS.wsgi.application"
LOGIN_URL = "login"

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",  # MariaDB uses the MySQL backend
        "NAME": "ltlms",  # Replace with your database name
        "USER": "manager",
        "PASSWORD": "manger@2025#",
        "HOST": "localhost",
        "PORT": "3307",
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Qatar"

USE_I18N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']  # Folder within your project directory for static files
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Folder for the collected static files
