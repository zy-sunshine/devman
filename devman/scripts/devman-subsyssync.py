#!/usr/bin/env python
import dircache, os, sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'devman.settings'
if 'DEVMAN_WORKDIR' not in os.environ:
    os.environ['DEVMAN_WORKDIR'] = os.path.abspath(os.getcwd())
workdir = os.environ['DEVMAN_WORKDIR']
print('Workdir = [%s]' % workdir)
import django
django.setup()

import devman.settings
from django.db import models
from devman.dmsubsys.models import DBSubsys, DBSubsysMember
from devman.dmsubsys.subsys import DMSubsysTypeMap, DMSubsysCheckDir

maxlevel = 1
for sstype in DMSubsysTypeMap.keys():
    # Scan all possible subsys with level limitation.
    level = 0
    subsysroot = os.path.join(workdir, sstype)
    subsyses = []
    curdirs = [subsysroot]
    while curdirs and level < maxlevel:
        newdirs = []
        for curdir in curdirs:
            for subfile in dircache.listdir(curdir):
                subpath = os.path.join(curdir, subfile)
                if not os.path.isdir(subpath): continue
                if DMSubsysCheckDir(sstype, subpath): subsyses.append(subpath)
                else: newdirs.append(subpath)
        curdirs = newdirs
        level = level + 1
    # Sync subsyses with DBSubsys.
    for robj in DBSubsys.objects.filter(sstype = sstype):
        robjpath = os.path.join(subsysroot, robj.relpath)
        if robjpath in subsyses: subsyses.remove(robjpath)
        else: # Remove the records for the disappeared subsys.
            print('Remove %s(%s)' % (robjpath, robj.sstype))
            DBSubsysMember.objects.filter(subsys = robj).delete()
            robj.delete()
    for subsys in subsyses: # Add records for the new added subsys.
        robj = DBSubsys(sstype = sstype,
                        relpath = os.path.relpath(subsys, subsysroot))
        robj.save()
        print('Add %s(%s)' % (subsys, sstype))
