import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(BASE_DIR))

from django.core.wsgi import get_wsgi_application

os.environ['DEVMAN_WORKDIR'] = '/home/devman'
os.environ["DJANGO_SETTINGS_MODULE"] = "devman.settings"

application = get_wsgi_application()
