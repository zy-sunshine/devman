#!/usr/bin/python
import urllib2
from devman.dmroot import _, MkKV
from devman.dmroot.models import DBMember, DBMemberPrefs, DBPerm,\
    DBMemberPerm, DBPermSubperm
from devman.dmroot.autoid import AutoLocalUID
#from devman.dmroot.log import SysLogList
from devman.dmroot.entity import EntityCheckMember

#class ExportUpdater(object):
#    def __init__(self):
#        pass
#
#    def match(self, perm):
#        return False
#
#    def update(self, diffs):
#        pass

#class MemberPermExporter(object):
#    def __init__(self):
#        self.mobjmap = {}
#
#    def MarkMember(self, mobj):
#        if mobj.id in self.mobjmap: return
#        self.mobjmap[mobj.id] = [mobj.member, mobj.getperms(), []]
#
#    def MarkPerms(self, perms):
#        for mrobj in DBMemberRoles.objects.filter(role = robj):
#            self.MarkMember(mrobj.member)
#
#    def Export(self):
#        from devman.perms import perm_updaters
#
#       mids = self.mobjmap.keys()
#        mids.sort()
#        # Get the change result.
#        for mid in mids:
#            mobjs = DBMember.objects.filter(id = mid)
#            if len(mobjs) > 0: self.mobjmap[mid][2] = mobjs[0].getperms()
#        # Get the perm diffs.
#        diffs = []
#        for mid in mids:
#            addset = []
#            delset = []
#            for perm in self.mobjmap[mid][1] + self.mobjmap[mid][2]:
#                # Skip all unmatched perms.
#                match = False
#                for updater in perm_updaters:
#                    if updater.match(perm): match = True; break
#                if not match: continue
#                # Fill delset/addset.
#                if perm in self.mobjmap[mid][1]:
#                    if perm not in self.mobjmap[mid][2]:
#                        delset.append(perm)
#                else:
#                    if perm in self.mobjmap[mid][2]:
#                        addset.append(perm)
#            if addset != [] or delset != []:
#                diffs.append((mid, self.mobjmap[mid][0], addset, delset))
#        # Run updaters.
#        for updater in perm_updaters:
#            # Skip all unrelated lines.
#            subdiffs = []
#            for diff in diffs:
#                subaddset = []
#                for perm in diff[2]:
#                    if updater.match(perm): subaddset.append(perm)
#                subdelset = []
#                for perm in diff[3]:
#                    if updater.match(perm): subdelset.append(perm)
#                if subaddset != [] or subdelset != []:
#                    subdiffs.append((diff[0], diff[1], subaddset, subdelset))
#            # Call update if related diffs found.
#            if subdiffs != []: updater.update(subdiffs)

def NewLocalMember(member, name = None, email = None, mobile = None):
    if name is None: name = member
    if email is None: email = '%s@unknown' % member
    if mobile is None: mobile = ''
    userid = AutoLocalUID.request()
    if userid is None: return None
    mobj = DBMember(member = member, sourceid = DBMember.LOCAL, name = name,
                    userid = userid, jobnum = userid, email = email,
                    mobile = mobile, enabled = True)
    return mobj

urlfmt = 'http://192.168.1.190:8090/magicsso/certify?orgname=hackos&code=%s'
def GetSsoMember(member):
    if not isinstance(member, DBMember): mobj = None
    else: mobj = member; member = mobj.member
    inf = urllib2.urlopen(urlfmt % member)
    info = inf.read().decode('GB18030').strip().split('|')
    inf.close()
    if len(info) != 10: return None
    if mobj is None:
        return DBMember(member = member, sourceid = DBMember.SSOAUTH,
                        name = info[3], userid = int(info[0]),
                        jobnum = int(info[1]), email = info[8],
                        mobile = info[9])
    mobj.name = info[3]
    mobj.userid = int(info[0])
    mobj.jobnum = int(info[1])
    mobj.email = info[8]
    mobj.mobile = info[9]
    return mobj

#def Member2Object(member):
#    if isinstance(member, DBMember): return member
#    if member[:5] == 'hackos\\': member = member[5:]
#    mobjs = DBMember.objects.filter(member = member)
#    if len(mobjs) > 0: return mobjs[0]
#    if trial or member == nologin:
#        mobj = NewLocalMember(member)
#        prompt = _('Local member')
#    else:
#        mobj = GetSsoMember(member)
#        prompt = _('Sso member')   
#    if mobj is None: return None
#    mobj.enabled = True
#    mobj.save()
#    logfmt = _('%(v0)s [%(v1)s] is added automatically')
#    SysLogList.log_member(mobj, logfmt % MkKV(prompt, mobj.name))
#    return mobj

def DelMember(mobj):
    if EntityCheckMember(mobj): return None
    mobjname = mobj.name
    DBMemberPrefs.objects.filter(member = mobj).delete()
    DBMemberPerm.objects.filter(member = mobj).delete()
    DisableMember(mobj)
    if mobj.sourceid == DBMember.LOCAL: AutoLocalUID.restore(mobj.userid)
    mobj.UserDel()
    mobj.delete()
    return mobjname

def DisableMember(mobj):
    mobj.enabled = False
    mobj.save()
    #exporter = MemberPermExporter()
    #exporter.MarkMember(mobj)
    #DBMemberRoles.objects.filter(member = mobj).delete()
    #exporter.Export()

#def UpdateMemberRole(mobj, roles):
#    exporter = MemberPermExporter()
#    exporter.MarkMember(mobj)
#    for checked, robj in roles:
#        exists = DBMemberRoles.objects.filter(member = mobj,
#                                              role = robj).exists()
#        if checked and not exists:
#            mrobj = DBMemberRoles(member = mobj, role = robj)
#            mrobj.save()
#        elif not checked and exists:
#            DBMemberRoles.objects.filter(member = mobj, role = robj).delete()
#    exporter.Export()

#def NewRole(newname, perms):
#    exporter = MemberPermExporter()
#    robj = DBRole(name = newname)
#    robj.save()
#    for checked, pobj in perms:
#        if not checked: continue
#        rpobj = DBRolePerms(role = robj, perm = pobj)
#        rpobj.save()
#    exporter.Export()

#def DelRole(robj):
#    exporter = MemberPermExporter()
#    exporter.MarkRole(robj)
#    DBMemberRoles.objects.filter(role = robj).delete()
#    DBRolePerms.objects.filter(role = robj).delete()
#    robj.delete()
#    exporter.Export()

#def UpdateRole(robj, perms):
#    exporter = MemberPermExporter()
#    exporter.MarkRole(robj)
#    for checked, pobj in perms:
#        exists = DBRolePerms.objects.filter(role = robj, perm = pobj).exists()
#        if checked and not exists:
#            rpobj = DBRolePerms(role = robj, perm = pobj)
#            rpobj.save()
#        elif not checked and exists:
#            DBRolePerms.objects.filter(role = robj, perm = pobj).delete()
#    exporter.Export()

#def UpdatePerms(delpobjs, newpnames):
#    exporter = MemberPermExporter()
#    for delpobj in delpobjs:
#        rpobjs = DBRolePerms.objects.filter(perm = delpobj)
#        for rpobj in rpobjs: exporter.MarkRole(rpobj.role)
#        for rpobj in rpobjs: rpobj.delete()
#        delpobj.delete()
#    for newpname in newpnames:
#        pobj = DBPerm(name = newpname)
#        pobj.save()
#    exporter.Export()
