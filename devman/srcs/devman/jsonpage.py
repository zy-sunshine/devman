#!/usr/bin/python
from devman.dmroot import _
from devman.dmroot.exceptions import DMException, DMUnsupportedError
from devman.dmroot.page import DMPage
import devman.dmroot.views
import devman.dmsubsys.views
import devman.dmproj.views

mapDMViews = {}
mapDMActions = {}
for module in (devman.dmroot.views,
               devman.dmsubsys.views,
               devman.dmproj.views
               ):
    for name, klass in module.__dict__.items():
        if not isinstance(klass, type): continue
        if name[:len('DMView')] == 'DMView': mapDMViews[name] = klass
        if name[:len('DMAction')] == 'DMAction': mapDMActions[name] = klass

def getDMViewObject(desc, params):
    if desc['klass'] not in mapDMViews:
        raise DMUnsupportedError, _('%s is not supported yet') % repr(desc['klass'])
    return mapDMViews[desc['klass']](desc, params)

def getDMActionObject(desc, params):
    if desc['klass'] not in mapDMActions:
        raise DMUnsupportedError, _('%s is not supported yet') % repr(desc['klass'])
    return mapDMActions[desc['klass']](desc, params)

def JsonPage(req):
    pageobj = DMPage(req, getDMViewObject, getDMActionObject)
#     try: pageobj.loadjson(req)
#     except DMException, exc: pageobj.set_failed(unicode(exc))
    pageobj.loadjson(req)
    return pageobj.response(req)
