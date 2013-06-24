#!/usr/bin/python
#from sys import path as syspath
#from os import write, readlink
from os import environ as osenv
from os.path import abspath, join, dirname
from django.core.handlers.wsgi import WSGIHandler

selflink = abspath(__file__)
#selfpy = abspath(readlink(__file__))
#write(2, 'DEVMAN_WORKDIR = [%s]\n' % osenv['DEVMAN_WORKDIR'])
#write(2, 'selflink = [%s]\n' % selflink)
#write(2, 'selfpy = [%s]\n' % selfpy)

#syspath.insert(0, abspath(join(selfpy, '..', '..', '..')))
osenv['DJANGO_SETTINGS_MODULE'] = 'devman.settings'
osenv['LC_ALL'] = 'zh_CN'
osenv['DEVMAN_WORKDIR'] = abspath(dirname(selflink))
application = WSGIHandler()
