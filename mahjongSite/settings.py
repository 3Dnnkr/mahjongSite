"""
Django settings for mahjongSite project.

Generated by 'django-admin startproject' using Django 3.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import os
import cloudinary
from django.contrib import messages

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# # SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'django-insecure-%%+q+fdwbv!+0+@lx5m_5n(6jl8r)x28cg&=v6ycpfo9&151h9'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["jtnnkr.herokuapp.com"]


# Application definition
INSTALLED_APPS = [
    'nnkr',
    'user',
    'wiki',
    'mdeditor',
    'social_django',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cloudinary',
]

# meditor setting
X_FRAME_OPTIONS = 'SAMEORIGIN'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mahjongSite.urls'

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
                'social_django.context_processors.backends', 
                'social_django.context_processors.login_redirect',
                'mahjongSite.context_processors.google_analytics',
                'mahjongSite.context_processors.active_user_num',
            ],
            'builtins':[
                'nnkr.templatetags.extra_tags'
            ],
        },
    },
]

WSGI_APPLICATION = 'mahjongSite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    # 'default': {
         # 'ENGINE': 'django.db.backends.sqlite3',
         # 'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
         # }
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nnkrdb',
        'USER': 'admin',
        'PASSWORD': 'ramanujan',
        'HOST': '',
        'PORT': '',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

# Static files are collected here by 'collectatatic' command.
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# User Authorization setting
AUTH_USER_MODEL = 'user.User'
LOGIN_URL = 'user:login'
LOGIN_REDIRECT_URL = 'nnkr:top'
LOGOUT_REDIRECT_URL = 'nnkr:top'


# Twitter Authorization setting
AUTHENTICATION_BACKENDS = [
    'social_core.backends.twitter.TwitterOAuth',
    'django.contrib.auth.backends.ModelBackend',
]
SOCIAL_AUTH_TWITTER_KEY = os.environ.get('SOCIAL_AUTH_TWITTER_KEY')
SOCIAL_AUTH_TWITTER_SECRET = os.environ.get('SOCIAL_AUTH_TWITTER_SECRET')
SOCIAL_AUTH_LOGIN_REDIRECT_URL = 'nnkr:top'


# Heroku database setting
import dj_database_url
db_from_env = dj_database_url.config()
DATABASES['default'].update(db_from_env)


# provide separation between Heroku and Local
try:
    from .local_settings import *
except ImportError:
    pass

if not DEBUG:
    import django_heroku
    django_heroku.settings(locals())


# Cloudinary Setting
cloudinary.config(
    cloud_name = os.environ.get('CLOUD_NAME'),
    api_key    = os.environ.get('CLOUDINARY_API_KEY'),
    api_secret = os.environ.get('CLOUDINARY_API_SECRET'),
)

# Message Setting
MESSAGE_TAGS = {
    messages.INFO: 'alert alert-info',
    messages.SUCCESS: 'alert alert-success',
    messages.WARNING: 'alert alert-warning',
    messages.ERROR: 'alert alert-danger',
}

# Google Analytics
GOOGLE_ANALYTICS_TRACKING_ID ='G-JZRES8R7S7'
#os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = BASE_DIR + '/ga4/client_secrets.json'
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', BASE_DIR + '/ga4/client_secrets.json')