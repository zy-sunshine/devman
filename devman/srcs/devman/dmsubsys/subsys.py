import dircache, os.path
from devman.dmroot.models import DBPerm, DBMemberPerm

class DMSubsysBase(object):
    def __init__(self, sstype, relpath, descs):
        self.sstype = sstype
        self.relpath = relpath
        self.descs = descs
        pobjs = DBPerm.objects.filter(name = sstype)
        if len(pobjs) == 0: self.pobj = None
        else: self.pobj = pobjs[0]

    def getlink(self, kwPage):
        rooturl0 = kwPage['rooturl0']
        return '%s/%s/%s' % (rooturl0, self.descs['url'], self.relpath)

    def getlinkname(self, kwPage):
        return self.getlink(kwPage)

    def permitted_members(self):
        if self.pobj is None: return []
        mpobjs = DBMemberPerm.objects.filter(perm = self.pobj)
        return map(lambda mpobj: mpobj.member, mpobjs)

class DMSubsysSVN(DMSubsysBase):
    pass

class DMSubsysGIT(DMSubsysBase):
    def getlink(self, kwPage):
        return None

    def getlinkname(self, kwPage):
        host = kwPage['host']
        if ':' in host: host = host.split(':')[0]
        return '%s@%s:%s' % (kwPage['mobj'].member, host, self.relpath)

class DMSubsysTrac(DMSubsysBase):
    pass

DMSubsysTypeMap = { 'svn': { 'klass': DMSubsysSVN,
                             'dirs': ('conf', 'db', 'hooks', 'locks'),
                             'files': ('format', 'README.txt'),
                             'optdirs': ('dav',) },
                    'git': { 'klass': DMSubsysGIT,
                             'dirs': ('hooks', 'info', 'objects', 'refs'),
                             'files': ('config', 'description', 'HEAD'),
                             'optfiles': ('packed-prefs',) },
                    'trac': { 'klass': DMSubsysTrac,
                              'dirs': ('conf', 'db', 'htdocs',
                                       'log', 'plugins', 'templates'),
                              'files': ('README', 'VERSION'),
                              'optdirs': ('files', 'attachments', 'chrome', 'cgi-bin') } }

def DMSubsysCheckDir(sstype, path):
    if sstype == 'git': return True
    ssmap = DMSubsysTypeMap[sstype]
    cnt = 0
    for subdir in ssmap['dirs']:
        if not os.path.isdir(os.path.join(path, subdir)): return False
    cnt = cnt + len(ssmap['dirs'])
    for subfile in ssmap['files']:
        if not os.path.isfile(os.path.join(path, subfile)): return False
    cnt = cnt + len(ssmap['files'])
    if 'optdirs' in ssmap:
        for subdir in ssmap['optdirs']:
            if not os.path.isdir(os.path.join(path, subdir)): continue
            cnt = cnt + 1
    if 'optfiles' in ssmap:
        for subfile in ssmap['optfiles']:
            if not os.path.isfile(os.path.join(path, subfile)): continue
            cnt = cnt + 1
    return len(dircache.listdir(path)) == cnt

def DMSubsysObject(dbobj, descs):
    klass = DMSubsysTypeMap[dbobj.sstype]['klass']
    return klass(dbobj.sstype, dbobj.relpath, descs)
