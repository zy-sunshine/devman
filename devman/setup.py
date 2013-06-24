#!/usr/bin/python
import glob, json, os, os.path
from distutils.core import setup

pkgdata = ['ver.json',
           os.path.join('templates', '*.html'),
           os.path.join('locale', 'zh_CN', 'LC_MESSAGES', 'django.mo'),
           os.path.join('workdir', 'config.json')]
incs_files = ('*.css', '*.js', 'djangopowered126x54.gif', 'watermark.png')
pkgdata.extend(map(lambda f: os.path.join('incs', f), incs_files))
for root, dirs, files in os.walk(os.path.join('devman', 'descs')):
    for f in files:
        if os.path.splitext(f)[-1] not in ('.json',): continue
        relroot = os.path.relpath(root, 'devman')
        pkgdata.append(os.path.join(relroot, f))

selfver = '0'
if os.path.exists(os.path.join('devman', 'ver.json')):
    selfver = str(json.load(open(os.path.join('devman', 'ver.json'), 'rt')))

setup(name = 'devman',
      version = selfver,
      author = 'Charles Wang',
      author_email = 'wangli01@snda.com',
      url = 'https://bbtrac.sdo.com:11554/dmprojs/trac/devman/trunk',
      description = 'Development manager for NutShell Electronics.',
      scripts = glob.glob(os.path.join('scripts', '*')),
      data_files = [('/etc/apache2/modules.d',
                     [os.path.join('confs', '91_devman.conf'),
                      os.path.join('confs', '91_devman_dev.conf')])],
      packages = ['devman',
                  'devman.dmroot',
                  'devman.dmsubsys',
                  'devman.dmproj',
                  'devman.nsaabill',
                  'devman.nstool',
                  'devman.nstask',
                  'devman.nscontact',
                  'devman.nsaxure',
                  'devman.nswiki',
		  'devman.nsattach',
		  'devman.nsfactest'],
      package_dir = { 'devman' : 'devman' },
      package_data = { 'devman' : pkgdata,
                       'devman.dmroot' : ['nstemp.txt'] },
      )
