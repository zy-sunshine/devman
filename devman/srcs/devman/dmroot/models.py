import hashlib, os.path
from devman.settings import ssoauthdir, superusers
from django.utils.translation import ugettext_lazy as _
from django.db import models
from devman.dmroot.ssoauth import SsoUsersAddOrEdit, SsoUsersDel

# Create your models here.

class DBIDValue(models.Model):
    idtypeid = models.PositiveIntegerField()
    val = models.PositiveIntegerField()

class DBIDScope(models.Model):
    idtypeid = models.PositiveIntegerField()
    minval = models.PositiveIntegerField()
    maxval = models.PositiveIntegerField()

def CmpDBMember(mobj0, mobj1):
    return cmp(mobj0.member, mobj1.member)

class DBMember(models.Model):
    member = models.CharField(max_length=64)
    sourceid = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=64)
    userid = models.PositiveIntegerField()
    jobnum = models.PositiveIntegerField()
    email = models.EmailField()
    mobile = models.CharField(max_length=11, blank = True, null = True)
    enabled = models.BooleanField()
    lastlogin = models.DateTimeField(blank = True, null = True)

    LOCAL = 1
    SSOAUTH = 2
    SIDALL = (None, (_('Local User'),), (_('SSO User'),))

    def getsource(self):
        return self.SIDALL[self.sourceid][0]

    def getperms(self, req_user_id=None, req_user_name=None):
        mpobjs = DBMemberPerm.objects.filter(member = self)
        npobjs = []
        for mpobj in mpobjs:
            if mpobj.perm not in npobjs: npobjs.append(mpobj.perm)
        pobjs = []
        while npobjs:
            nnpobjs = []
            for npobj in npobjs:
                if npobj in pobjs: continue
                for nnpobj in DBPermSubperm.objects.filter(perm = npobj):
                    if nnpobj in pobjs: continue
                    if nnpobj in npobjs: continue
                    if nnpobj in nnpobjs: continue
                    nnpobjs.append(nnpobj)
            pobjs.extend(npobjs)
            npobjs = nnpobjs
        perms = map(lambda pobj: pobj.name, pobjs)
        if self.member in superusers and 'super' not in perms:
            perms.append('super')
        if req_user_id is not None and int(req_user_id) == self.id:
            perms.append('self')
        if req_user_name is not None and req_user_name == self.member:
            perms.append('self')
        return perms

    def UserAddOrEdit(self, pwd = ''):
        if self.sourceid == self.LOCAL: usertype = 'l'
        elif self.sourceid == self.SSOAUTH: usertype = 's'
        else: return
        enchexpwd = hashlib.md5(pwd).hexdigest().upper()
        SsoUsersAddOrEdit(usertype, self.userid, self.member, enchexpwd)

    def UserDel(self):
        SsoUsersDel(self.member)

class DBMemberPrefs(models.Model):
    member = models.ForeignKey(DBMember)
    theme = models.CharField(max_length=64)

def CmpDBPerm(pobj0, pobj1):
    return cmp(pobj0.name, pobj1.name)

class DBPerm(models.Model):
    name = models.CharField(max_length=64)

class DBPermSubperm(models.Model):
    perm = models.ForeignKey(DBPerm, related_name = 'perm')
    subperm = models.ForeignKey(DBPerm, related_name = 'subperm')

class DBMemberPerm(models.Model):
    member = models.ForeignKey(DBMember)
    perm = models.ForeignKey(DBPerm)

class DBHome(models.Model):
    homedir = models.CharField(max_length = 64)

maxlen_string = 256
maxlen_textpiece = 256

class DBEntity(models.Model):
    parent = models.PositiveIntegerField(blank = True, null = True)
    klass = models.CharField(max_length = 64)
    owner = models.ForeignKey(DBMember)
    create_date = models.DateTimeField()
    lastedit_date = models.DateTimeField()
    home = models.ForeignKey(DBHome, blank = True, null = True)

class DBAttrPositiveInteger(models.Model):
    entity = models.ForeignKey(DBEntity)
    attr = models.PositiveSmallIntegerField()
    value = models.PositiveIntegerField()

class DBAttrInteger(models.Model):
    entity = models.ForeignKey(DBEntity)
    attr = models.PositiveSmallIntegerField()
    value = models.IntegerField()

class DBAttrString(models.Model):
    entity = models.ForeignKey(DBEntity)
    attr = models.PositiveSmallIntegerField()
    value = models.CharField(max_length = maxlen_string)

class DBAttrDateTime(models.Model):
    entity = models.ForeignKey(DBEntity)
    attr = models.PositiveSmallIntegerField()
    value = models.DateTimeField()

class DBAttrMember(models.Model):
    entity = models.ForeignKey(DBEntity)
    attr = models.PositiveSmallIntegerField()
    value = models.ForeignKey(DBMember)

class DBCommentText(models.Model):
    entity = models.ForeignKey(DBEntity)
    idx = models.PositiveIntegerField()
    value = models.CharField(max_length = maxlen_textpiece)

class DBCommentCachedText(models.Model):
    entity = models.ForeignKey(DBEntity)
    idx = models.PositiveIntegerField()
    value = models.CharField(max_length = maxlen_textpiece)
