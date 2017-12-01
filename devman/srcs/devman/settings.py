# Django settings for devman project.
import glob, json, os.path

devmanroot = os.path.abspath(os.path.dirname(__file__))
descroot = 'descs'
selfverfn = os.path.join(devmanroot, 'ver.json')
if not os.path.exists(selfverfn): selfver = 0
else: selfver = int(json.load(open(selfverfn, 'rt')))
rsttempfn = os.path.join(devmanroot, 'dmroot', 'dmtemp.txt')
incsdir = os.path.join(devmanroot, 'incs')

workdir = os.environ.get('DEVMAN_WORKDIR',
                         os.path.join(devmanroot, 'workdir'))

descdir = os.path.join(devmanroot, descroot)
pagedir = os.path.join(descdir, 'pages')
taskdir = os.path.join(descdir, 'tasks')

if not os.path.exists(os.path.join(workdir, 'config.json')): configjson = {}
else: configjson = json.load(open(os.path.join(workdir, 'config.json'), 'rt'))

trial = configjson.get('trial', True)
logresp = configjson.get('logresp', False)
nologin = configjson.get('nologin', 'nobody')
superusers = configjson.get('superusers', ('admin',))

ssoauthdir = configjson.get('ssoauthdir', os.path.join(workdir, 'ssoauth'))
if not ssoauthdir:
    ssoauthdir = os.path.join(workdir, 'ssoauth')
    
entityroot_id = configjson.get('entityroot_id', 1)
topsyslists = configjson.get('topsyslists', None)

def load_taskjsonfile(taskjsonfile):
    taskjson = json.load(open(taskjsonfile, 'rt'))
    taskjson['klass'] = os.path.splitext(os.path.basename(taskjsonfile))[0]
taskjsons = map(lambda taskjsonfile: load_taskjsonfile(taskjsonfile),
                glob.glob(os.path.join(taskdir, '*.json')))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = configjson.get('db')

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = configjson.get('timezone')

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = configjson.get('language-code')

_ = lambda s: s

LANGUAGES = (
    ('en-us', _('English')), 
    ('zh-hans', _('Chinese')),
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = workdir

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = "/mymedia/"

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = "/media/"

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'a=oilx$mci_fr2al9++9+u91xbipp31wuy(o@5rx+ckwf4ez18'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = "devman.urls"

TEMPLATE_DIRS = (
    os.path.join(devmanroot, "templates"),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'devman.dmroot',
    'devman.dmsubsys',
    'devman.dmproj',
)

STATIC_PATH = os.path.join(devmanroot, "incs")
TEMPLATES_PATH = os.path.join(devmanroot, "templates")
WIKI_ATTACHMENTS_ROOT = os.path.join(workdir, 'attachments')

STATIC_URL = '/static/'

# Bytes! Default: 1 MB.
WIKI_ATTACHMENTS_MAX = 2 * 1024 * 1024
ALLOWED_HOSTS=['*', ]
