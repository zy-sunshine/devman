#!/usr/bin/python
import os, sys
#from django.core.management import execute_manager

os.environ['DJANGO_SETTINGS_MODULE'] = 'devman.settings'
if 'DEVMAN_WORKDIR' not in os.environ:
    os.environ['DEVMAN_WORKDIR'] = os.path.abspath(os.getcwd())
print('Workdir = [%s]' % os.environ['DEVMAN_WORKDIR'])
import devman.settings
from django.db import models
#execute_manager(devman.settings, argv = [sys.argv[0], 'syncdb', '--database=newdb'])

#sys.path.insert(0, 'devman')

import devman.dmroot.models
import devman.dmproj.models

# Scan all model files.
allKlasses = [devman.dmroot.models.DBMember,
              devman.dmroot.models.DBEntity]
for module in (devman.dmroot.models,
               devman.dmproj.models):
    for name, klass in module.__dict__.items():
        if not isinstance(klass, type): continue
        if not issubclass(klass, models.Model): continue
        if klass in allKlasses: continue
        allKlasses.append(klass)

#for klass in allKlasses:
#    print('Class: [%s]' % klass.__name__)
#    print('Cleanup %s' % klass.__name__)
#    klass.objects.using('newdb').all().delete()
#    pass

for klass in allKlasses:
    cnt = 0
    for dbobj in klass.objects.using('default').all():
        cnt = cnt + 1
        print 'Migrate %s ... %u\r' % (klass.__name__, cnt),
        sys.stdout.flush()
        dbobj.save(using = 'newdb')
    print('Migrate %s with %u row(s)' % (klass.__name__, cnt))

print('Done')

