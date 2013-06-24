from django.core.paginator import Paginator
from django.utils.translation import gettext, ugettext_lazy as _
from datetime import datetime

monthfmt = '%Y-%m'
datefmt = '%Y-%m-%d'
timefmt = '%H:%M:%S'
datetimefmt = '%Y-%m-%d %H:%M:%S'
datestart = datetime.strptime('2011-01-01', datefmt)

def J_(text):
    v = ("{%_('", "')%}")
    if text[:len(v[0])] != v[0]: return text
    if text[-len(v[1]):] != v[1]: return text
    return _(text[len(v[0]) : -len(v[1])])
    
def J_DICT(dictobj, k, defval):
    if k not in dictobj: return defval
    return J_(dictobj[k])

def MkKV(*arg):
    kv = {}
    for idx in range(len(arg)): kv['v%u' % idx] = arg[idx]
    return kv

def MkROW(objlist, width):
    objrowlist = []
    objrow = []
    for obj in objlist:
        objrow.append(obj)
        if len(objrow) < width: continue
        objrowlist.append(objrow)
        objrow = []
    if len(objrow) > 0:
        while len(objrow) < width: objrow.append(None)
        objrowlist.append(objrow)
    return objrowlist

def MkROW0(objlist, width):
    if objlist == []: return [None] * width, []
    objrowlist = MkROW(objlist, width)
    return objrowlist[0], objrowlist[1:]
    
def paging(objects, rowspage, page):
    paginator = Paginator(objects, rowspage)
    try: obj = paginator.page(page)
    except: obj = paginator.page(paginator.num_pages)
    return obj

def getRequireIDName(id_):
    if id_ is None or id_ == u'': return ''
    ids = id_.split('-')
    name = ids[0].split('_')[1] + '-' + ids[1].split('_')[2]
    return name
