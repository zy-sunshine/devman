import os.path
from django.db import models
from devman.settings import ssoauthdir
from devman.dmroot.models import DBMember
from devman.dmroot.ssoauth import SsoUsersGet, SsoUsersSet,\
    SsoAccessGet, SsoAccessSet

class DBSubsys(models.Model):
    sstype = models.CharField(max_length = 16) # svn/git/trac
    relpath = models.CharField(max_length = 256)

    def sschar(self):
        return DBSubsys.ConvertTypeToChar(self.sstype)

    @staticmethod
    def ConvertTypeToChar(typ):
        if typ == 'svn': return 's'
        elif typ == 'git': return 'g'
        elif typ == 'trac': return 't'
        elif typ == 'proposal': return 'p'
        return None

def CmpDBSubsysMember(smobj0, smobj1):
    return cmp(smobj0.member.member, smobj1.member.member)

class DBSubsysMember(models.Model):
    subsys = models.ForeignKey(DBSubsys)
    member = models.ForeignKey(DBMember)
    ipaddr = models.CharField(max_length = 16, blank = True, null = True)

def UpdateSsoRecords(ssobj, addmobjs, rmmobjs):
    membersmap = {}
    addmap = {}
    smobjs = DBSubsysMember.objects.values('member').distinct()
    for smobj in smobjs:
        mobjs = DBMember.objects.filter(id = smobj['member'])
        if len(mobjs) == 0: continue
        membersmap[mobjs[0].member] = mobjs[0]
        addmap[mobjs[0].member] = mobjs[0]

    # Update ssousers.txt
    ssousers_fn = os.path.join(ssoauthdir, 'ssousers.txt')
    if not os.path.isfile(ssousers_fn): ssouserslns = []
    else: ssouserslns = open(ssousers_fn, 'rt').read().splitlines()
    writeset = []
    for ln in ssouserslns:
        userkw = SsoUsersGet(ln)
        if userkw['user'] not in membersmap: continue
        writeset.append(ln)
        del(addmap[userkw['user']])
    for mobj in addmap.values():
        if mobj.sourceid == DBMember.LOCAL: utype = 'l'
        elif mobj.sourceid == DBMember.SSOAUTH: utype = 's'
        else: continue # Skip unsupported sourceid.
        writeset.append(SsoUsersSet(utype, mobj.userid, mobj.member, getattr(mobj, 'enchexpwd', '')))
    if writeset: open(ssousers_fn, 'wt').write('\n'.join(writeset) + '\n')
    else: open(ssousers_fn, 'wt').write('')

    # Update ssoaccess.txt
    writeset = []
    ssoaccess_fn = os.path.join(ssoauthdir, 'ssoaccess.txt')
    if not os.path.isfile(ssoaccess_fn):
        # Generated new ssoaccess.txt
        for smobj in DBSubsysMember.objects.all():
            sschar = smobj.subsys.sschar()
            if not sschar: continue
            writeset.append(SsoAccessSet(sschar, smobj.member.member,
                                         smobj.ipaddr, smobj.subsys.relpath))
    else:
        sschar = ssobj.sschar()
        ssoaccesslns = open(ssoaccess_fn, 'rt').read().splitlines()
        rmmembers = map(lambda rmmobj: rmmobj.member, rmmobjs)
        for ln in ssoaccesslns:
            accesskw = SsoAccessGet(ln)
            if accesskw['subsys'] == ssobj.relpath and \
                    accesskw['sstype'] == sschar and \
                    accesskw['user'] in rmmembers:
                continue
            writeset.append(ln)
        for mobj in addmobjs:
            if not sschar: continue
            writeset.append(SsoAccessSet(sschar, mobj.member, '', ssobj.relpath))
    if writeset: open(ssoaccess_fn, 'wt').write('\n'.join(writeset) + '\n')
    else: open(ssoaccess_fn, 'wt').write('')
