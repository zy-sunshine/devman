import json, os.path
from devman.settings import pagedir
from devman.dmroot.models import DBMemberPerm, DBHome
from devman.dmroot.exceptions import DMJsonDescMissedError, DMJsonDescError

class DMUrlConf(object):
    def __init__(self, reqpath):
        self.homedir = '.'
        self.permset = ['super']
        self.dirs = self.pathsplit(reqpath)
        self.params = []
        self.descs = self.load()

    def pathsplit(self, path):
        dirs = []
        while path != '' and path != '/':
            path, d = os.path.split(path)
            dirs.insert(0, d)
        return dirs

    def load(self):
        urlpath = '/'.join(self.dirs)
        curpath = pagedir
        self.loadconf(curpath)
        jsonpath = None
        for idx in range(len(self.dirs)):
            if self.dirs[idx].split('.')[-1] == 'conf':
                raise DMJsonDescMissedError,\
                    '[%s] is reserved for system.' % urlpath
            subpath0 = os.path.join(curpath, self.dirs[idx])
            subpath1 = os.path.join(curpath, '%s.json' % self.dirs[idx])
            subpath2 = os.path.join(curpath, 'param.json')

            if os.path.isdir(subpath0):
                curpath = subpath0
            elif os.path.isfile(subpath1):
                jsonpath = subpath1
                self.params.extend(self.dirs[idx + 1:])
                break
            elif os.path.isfile(subpath2):
                jsonpath = subpath2
                self.params.extend(self.dirs[idx:])
                break
            else:
                raise DMJsonDescMissedError, '[%s] is missed' % urlpath
            self.loadconf(curpath)
        if jsonpath is None:
            subpath0 = os.path.join(curpath, 'index.json')
            if os.path.isfile(subpath0): jsonpath = subpath0
            else:
                raise DMJsonDescMissedError, '[%s] is missed' % urlpath
        try: descs = json.load(open(jsonpath, 'rt'))
        except ValueError, exc: raise DMJsonDescError, str(exc)
        return descs

    def loadconf(self, path):
        ucfpath = os.path.join(path, 'url.conf.json')
        if not os.path.isfile(ucfpath): return
        try: descs = json.load(open(ucfpath, 'rt'))
        except ValueError, exc: raise DMJsonDescError, str(exc)
        if descs.get('homeurl', False):
            self.homedir = os.path.relpath(path, pagedir)
        self.permset = descs.get('permset', self.permset)

    def check_perm(self, mobj):
        if self.permset in (True, False): return self.permset
        if 'super' in mobj.getperms(): return True
        for mpobj in DBMemberPerm.objects.filter(member = mobj):
            if mpobj.perm.name in self.permset: return True
        return False

    def get_homeurl(self, rooturl):
        if self.homedir == '.': return rooturl
        return '%s/%s' % (rooturl, self.homedir)

    def get_dbhomeobj(self):
        hobjs = DBHome.objects.filter(homedir = self.homedir)
        if len(hobjs) > 0: return hobjs[0]
        hobj = DBHome(homedir = self.homedir)
        hobj.save()
        return hobj
