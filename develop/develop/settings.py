import os
import dj_database_url

from pathlib import Path
from iso4217 import Currency
from vendorpromo.__version__ import VERSION
from django.utils.translation import ugettext_lazy as _

BUILD_VERSION = VERSION
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

SITE_ID = int(os.getenv('SITE_ID', '1'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '&1mmk1e%&9p87fvr=&v84u6fx1)$7f&%)*t9#$zfnu$#h#+5v^'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

LOGIN_REDIRECT_URL = '/'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'core',
    'crispy_forms',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'iso4217',
    'siteconfigs',
    'vendor',
    'vendorpromo',
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

ROOT_URLCONF = 'develop.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ os.path.join(BASE_DIR, 'templates') ],
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

WSGI_APPLICATION = 'develop.wsgi.application'


AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases


DATABASES = {}
DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=False, default=os.environ.get('DATABASE_URL', 'sqlite:///{}'.format(os.path.join(BASE_DIR, 'db.sqlite3'))))     # Default to SQLite for testing on GitHub


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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

FIXTURE_DIRS = (
   os.path.join(BASE_DIR, 'fixtures'),
)
# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = 'static_root/'

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

# Django Vendor Settings
VENDOR_PRODUCT_MODEL = 'core.Product'
VENDOR_PAYMENT_PROCESSOR = os.getenv("VENDOR_PAYMENT_PROCESSOR", "base.PaymentProcessorBase")
VENDOR_STATE = os.getenv("VENDOR_STATE", "DEBUG")
DEFAULT_CURRENCY = Currency.usd.name
AVAILABLE_CURRENCIES = {'usd': _('USD Dollars'), 'mxn': _('Mexican peso'), 'jpy': _('Japanese yen')}

VENDOR_COUNTRY_CHOICE = [
    'US',
    'JP',
    'MX'
]

VENDOR_COUNTRY_DEFAULT = 'US'

# Vendor Promo Settings
VENDOR_PROMO_PROCESSOR = os.getenv("VENDOR_PROMO_PROCESSOR", "base.PromoProcessorBase")
VENDOR_PROMO_PROCESSOR_URL = os.getenv("VENDOR_PROMO_PROCESSOR_URL")
VENDOR_PROMO_PROCESSOR_BARRER_KEY = os.getenv("VENDOR_PROMO_PROCESSOR_BARRER_KEY")
# Authorize.Net Settings:
AUTHORIZE_NET_API_ID = os.getenv("AUTHORIZE_NET_API_ID")
AUTHORIZE_NET_TRANSACTION_KEY = os.getenv("AUTHORIZE_NET_TRANSACTION_KEY")
AUTHORIZE_NET_SIGNITURE_KEY = os.getenv("AUTHORIZE_NET_SIGNITURE_KEY")
AUTHORIZE_NET_KEY = os.getenv("AUTHORIZE_NET_KEY")
AUTHORIZE_NET_TRANSACTION_TYPE_DEFAULT = os.getenv("AUTHORIZE_NET_TRANSACTION_TYPE_DEFAULT")