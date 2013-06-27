#!/usr/bin/python
import glob, json, os, os.path
from distutils.core import setup

pkgdata = ['ver.json',
           os.path.join('templates', '*.html'),
           os.path.join('locale', 'zh_CN', 'LC_MESSAGES', 'django.mo'),
           os.path.join('workdir', 'config.json')]
incs_files = ('*.css', '*.js', 'djangopowered126x54.gif')
pkgdata.extend(map(lambda f: os.path.join('incs', f), incs_files))
for root, dirs, files in os.walk(os.path.join('srcs/devman', 'descs')):
    for f in files:
        if os.path.splitext(f)[-1] not in ('.json',): continue
        relroot = os.path.relpath(root, 'srcs/devman')
        pkgdata.append(os.path.join(relroot, f))

selfver = '0'
if os.path.exists(os.path.join('srcs/devman', 'ver.json')):
    selfver = str(json.load(open(os.path.join('srcs/devman', 'ver.json'), 'rt')))

setup(name = 'devman',
      version = selfver,
      author = ('Charles Wang', 'Zhang Yang'),
      author_email = ('charlesw1234@163.com', 'zy.netsec@gmail.com'),
      url = 'https://github.com/zy-sunshine/devman',
      description = 'Development management system.',
      scripts = glob.glob(os.path.join('scripts', '*')),
      data_files = [('/etc/apache2/mods-enabled',
                     [os.path.join('confs', '91_devman.conf'),
                      os.path.join('confs', '91_devman_dev.conf')])],
      packages = ['devman',
                  'devman.dmroot',
                  'devman.dmsubsys',
                  'devman.dmproj',
          ],
      package_dir = { 'devman' : 'srcs/devman' },
      package_data = { 'devman' : pkgdata,
                       'devman.dmroot' : ['nstemp.txt'] },
      )

