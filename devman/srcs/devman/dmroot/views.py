#!/usr/bin/python
import glob, os.path
from datetime import datetime
from devman.settings import trial, incsdir
from devman.dmroot import _, J_, datefmt, datetimefmt, MkROW, MkROW0, MkKV
from devman.dmroot.exceptions import DMPermissionError, DMParamError
from devman.dmroot.view import DMView, DMViewConfirm, DMAction
from devman.dmroot.models import DBMember, CmpDBMember, DBMemberPrefs,\
    DBPerm, CmpDBPerm, DBPermSubperm, DBMemberPerm
from devman.dmroot.member import NewLocalMember, GetSsoMember,\
    DelMember, DisableMember
from devman.dmroot.log import getLogger
from hashlib import md5

class DMViewLogin(DMView):
    def __init__(self, desc, params):
        DMView.__init__(self, desc, params)
        self.width = 2
        self.template = 'view.login.html'
        self.reqctx = True
        self.needmobj = False

class DMViewLogWeeks(DMView):
    def __init__(self, desc, params):
        DMView.__init__(self, desc, params)
        self.width = desc.get('width', 5)
        self.template = 'view.log.weeks.html'

    def render(self, kwPage, req, desc):
        weekrows = MkROW(getLogger().render_urls(kwPage['homeurl'],
                                                desc['render']), self.width)
        return { 'weekrows': weekrows }

class DMViewLog(DMView):
    def __init__(self, desc, params):
        DMView.__init__(self, desc, params)
        self.width = 4
        if len(params) == 0: self.curdate = datetime.now()
        else:
            try: self.curdate = datetime.strptime(params[0], datefmt)
            except ValueError: self.curdate = datetime.now()
        self.template = 'view.log.html'

    def render(self, kwPage, req, desc):
        logdates = getLogger().render_subs_insteps(desc['render'], self.curdate, kwPage['hobj'])
        return { 'logdates': logdates }

class DMViewLogPanel(DMViewLog):
    def render(self, kwPage, req, desc):
        logdates = getLogger().render_subs_insteps(desc['render'], self.curdate, kwPage['hobj'])
        if len(logdates) > 0:
            logdates[0]['entities'] = logdates[0]['entities'][:desc['shownums']]
        moreurl = desc['moreurl'] % {'homeurl': kwPage['homeurl']}
        return { 'logdates': logdates,
                 'title': J_(desc.get('title', '')),
                 'moreurl': moreurl }

from devman.dmproj.views import getProjLinks
class DMViewMyProjectsPanel(DMView):
    def __init__(self, desc, params):
        DMView.__init__(self, desc, params)
        self.width = 6
        self.template = 'view.proj.list.html'

    def render(self, kwPage, req, desc):
        projs = getProjLinks(kwPage)
        return { 'projs': projs }

class DMViewMemberNewLocal(DMView):
    def __init__(self, desc, params):
        DMView.__init__(self, desc, params)
        self.width = 2
        self.template = 'view.member.new.local.html'
        self.reqctx = True

    def validate(self, kwPage, req, desc):
        return kwPage['is_super']

    def render(self, kwPage, req, desc):
        return { 'SID_LOCAL': DBMember.LOCAL }

class DMViewMemberNewSso(DMView):
    def __init__(self, desc, params):
        DMView.__init__(self, desc, params)
        self.width = 2
        self.template = 'view.member.new.sso.html'
        self.reqctx = True

    def validate(self, kwPage, req, desc):
        return kwPage['is_super']

    def render(self, kwPage, request, desc):
        return { 'SID_SSOAUTH': DBMember.SSOAUTH }

mscopes = ('a-c', 'd-f', 'g-i', 'j-l', 'm-o', 'p-s', 't-v', 'w', 'x-y', 'z')

class DMViewMemberScope(DMView):
    def __init__(self, desc, params):
        DMView.__init__(self, desc, params)
        self.width = len(mscopes)
        self.template = 'view.member.scope.html'

    def render(self, kwPage, req, desc):
        scopes = []
        for ms in mscopes:
            sc = { 'prompt': ms,
                   'url': '%s/member/scope/%s' % (kwPage['homeurl'], ms) }
            scopes.append(sc)
        return { 'scopes': scopes }

class DMViewMemberList(DMView):
    def __init__(self, desc, params):
        DMView.__init__(self, desc, params)
        self.enable_width = 10
        self.row_width = desc.get('row_width', 5)
        self.disable_width = 2
        if len(params) == 0: self.scope = mscopes[0]
        else:
            self.scope = params[0]
        if len(self.scope) == 1:
            self.scope = (self.scope[0], chr(ord(self.scope[0]) + 1))
        elif len(self.scope) == 3 and self.scope[1] == '-':
            self.scope = (self.scope[0], chr(ord(self.scope[2]) + 1))
        else:
            raise DMParamError, _('scope must be "%%c-%%c", not %s') % repr(params[0])
        self.members = None
        self.disables = None

    def is_disable(self, desc):
        return 'type' in desc and desc['type'] == 'disables'

    def _render_self(self, kw, req, desc):
        self.members = []
        self.disables = []
        for mobj in DBMember.objects.filter(member__gte = self.scope[0],
                                            member__lt = self.scope[1]):
            mval = { 'id': mobj.id, 'member': mobj.member,
                     'name': mobj.name, 'source': mobj.getsource(),
                     'mobile': mobj.mobile }
            if not mobj.lastlogin: mval['lastlogin'] = 'N/A'
            else:  mval['lastlogin'] = mobj.lastlogin.strftime(datetimefmt)
            if not mobj.enabled:
                if not kw['is_super']: mval['enableurl'] = None
                else: mval['enableurl'] = '%s/member/enable/%u' % (kw['homeurl'], mobj.id)
                self.disables.append(mval)
                continue
            permskw = []
            for mpobj in DBMemberPerm.objects.filter(member = mobj):
                permskw.append({ 'name': mpobj.perm.name,
                                 'url': '%s/perm' % kw['homeurl']})
            mval['perms'], mval['permrows'] = MkROW0(permskw, self.row_width)
            mval['rows'] = len(mval['permrows']) + 1
            mval['viewurl'] = '%s/member/view/%u' % (kw['homeurl'], mobj.id)
            opers = []
            opers.append(('delcfm', kw['is_super']))
            opers.append(('edit', kw['is_super'] or kw['mobj'].id == mobj.id))
            opers.append(('disable', kw['is_super']))
            for oper in opers:
                if not oper[1]: mval[oper[0] + 'url'] = None
                else: mval[oper[0] + 'url'] = '%s/member/%s/%u' %\
                        (kw['homeurl'], oper[0], mobj.id)
            self.members.append(mval)

    def render(self, kwPage, req, desc):
        if self.members is None or self.disables is None:
            self._render_self(kwPage, req, desc)
        if self.is_disable(desc):
            self.width = self.disable_width
            self.template = 'view.member.list.disables.html'
            return { 'disables': self.disables }
        else:
            self.width = self.enable_width
            self.template = 'view.member.list.html'
            return { 'members': self.members,
                     'row_width': self.row_width }

class DMViewMemberPublic(DMView):
    def __init__(self, desc, params):
        DMView.__init__(self, desc, params)
        reqmid = int(params[0])
        reqmobjs = DBMember.objects.filter(id = reqmid)
        if len(reqmobjs) == 0:
            raise DMParamError, _('Unknown member id: %u') % reqmid
        self.reqmobj = reqmobjs[0]

    def render(self, kwPage, req, desc):
        self.is_self = self.reqmobj.id == kwPage['mobj'].id
        self.is_local = self.reqmobj.sourceid == DBMember.LOCAL
        return { 'reqmobj': self.reqmobj,
                 'reqmobj_source': self.reqmobj.getsource() }

class DMViewMemberPrefs(DMViewMemberPublic):
    def __init__(self, desc, params):
        DMViewMemberPublic.__init__(self, desc, params)
        self.width = 2
        self.template = 'view.member.prefs.html'
        self.reqctx = True
        self.url_user_id = params and params[0] or None

    def render(self, kwPage, req, desc):
        kwView = DMViewMemberPublic.render(self, kwPage, req, desc)
        kwView['editor'] = kwPage['is_super'] or self.is_self
        kwView['local_editor'] = kwView['editor'] and self.is_local
        if kwView['editor']:
            kwView['themes'] = []
            themefns = glob.glob(os.path.join(incsdir, 'theme.*.css'))
            themefns.sort()
            for themefn in themefns:
                theme = os.path.basename(themefn).split('.')[1]
                if theme != kwPage['mobj_theme']: checked = ''
                else: checked = 'checked'
                kwView['themes'].append({ 'value': theme,
                                          'checked': checked,
                                          'label': theme })
        return kwView

class DMViewMemberPerms(DMViewMemberPublic):
    def __init__(self, desc, params):
        DMViewMemberPublic.__init__(self, desc, params)
        self.row_width = desc.get('width', 5)
        self.width = self.row_width
        self.template = 'view.subperm.html'
        self.reqctx = True

    def render(self, kwPage, req, desc):
        kwView = DMViewMemberPublic.render(self, kwPage, req, desc)
        kwView['row_width'] = self.row_width
        kwView['editable'] = kwPage['is_super'] or self.is_self
        if kwView['editable']:
            kwView['actionurl'] = '%s/member/permedit/%u' % (kwPage['homeurl'], self.reqmobj.id)
        kwView['title0'] = _('Current Permissions of Member [%s]') % self.reqmobj.name
        kwView['title1'] = _('Avaiable Permissions of Member [%s]') % self.reqmobj.name

        subperms0 = []
        pobjs0 = map(lambda mpobj: mpobj.perm,
                     DBMemberPerm.objects.filter(member = self.reqmobj))
        pobjs0.sort(cmp = CmpDBPerm)
        for pobj in pobjs0:
            subperms0.append({ 'name': pobj.name,
                               'check': 'PERM_CHECK_%u' % pobj.id })
        kwView['subperms0'] = MkROW(subperms0, self.row_width)

        subperms1 = []
        pobjs = DBPerm.objects.all().order_by('name')
        for pobj in pobjs:
            if pobj in pobjs0: continue
            subperms1.append({ 'name': pobj.name,
                               'check': 'PERM_CHECK_%u' % pobj.id })
        kwView['subperms1'] = MkROW(subperms1, self.row_width)
        return kwView

class DMActionMemberNew(DMAction):
    def is_valid_member_name(self, name):
        testname = name
        for ch in '_-.': testname = testname.replace(ch, '0')
        return testname.isalnum()
        
    def action(self, kw, req, desc):
        member = req.POST.get('NEW_MEMBER_LOGIN', '')
        if member == '':
            raise DMParamError, _('Member login name is not provided.')
        if DBMember.objects.filter(member = member).exists():
            raise DMParamError, _('Member [%s] exists already.') % member
        member0 = member.replace('.', '0')
        if not self.is_valid_member_name(member0):
            raise DMParamError, _('[%s] is not match [A-Za-z\.]+.') % member
        sid = int(req.POST.get('NEW_MEMBER_SID', str(DBMember.LOCAL)))
        if sid == DBMember.LOCAL:
            name = req.POST.get('NEW_MEMBER_NAME', '')
            if name == '': name = member
            pwd = req.POST.get('NEW_MEMBER_PWD', '')
            pwdcfm = req.POST.get('NEW_MEMBER_PWDCFM', '')
            email = req.POST.get('NEW_MEMBER_EMAIL', '')
            mobile = req.POST.get('NEW_MEMBER_MOBILE', '')
            if pwd != pwdcfm:
                raise DMParamError, _('Password and Password Confirm are not equal.')
            mobj = NewLocalMember(member, name = name, email = email, mobile = mobile)
            if mobj is None:
                raise DMParamError, _('New local member "%s" failed.') % member
            mobj.save()
            mtype = _('Local member')
        elif sid == DBMember.SSOAUTH:
            mobj = GetSsoMember(member)
            if mobj is None:
                raise DMParamError, _('Fetch sso member "%s" failed, the user may be not exists yet.') % member
            mobj.save()
            pwd = ''
            mtype = _('Sso member')
        mobj.UserAddOrEdit(pwd = pwd)
        logfmt = _('%(v0)s [%(v1)s] is added by [%(v2)s]')
        getLogger().log_member(kw['mobj'], kw['hobj'],
                              logfmt % MkKV(mtype, mobj.name, kw['mobj'].name))
        return DMAction.action(self, kw, req, desc) 
 
class DMActionMemberPublic(DMAction):
    def __init__(self, desc, params):
        DMAction.__init__(self, desc, params)
        self.memid = int(params[-1])
        memobjs = DBMember.objects.filter(id = self.memid)
        if len(memobjs) == 0:
            raise DMParamError, _('Unknown member id: %u') % self.memid
        self.memobj = memobjs[0]
   
    def check_perm(self, kw):
        if not kw['is_super']:
            raise DMPermissionError, _('No permission to do this.')

class DMViewMemberDeleteConfirm(DMViewConfirm):
    def __init__(self, desc, params):
        DMViewConfirm.__init__(self, desc, params)
        self.reqmid = int(params[-1])

    def get_prompt(self, kwPage, req, desc):
        reqmobjs = DBMember.objects.filter(id = self.reqmid)
        return _('Do you really want to delete "%s"?') % (reqmobjs[0].member)

    def get_confirm_url(self, kwPage, req, desc):
        return '%s/member/del/%u' % (kwPage['homeurl'], self.reqmid)

    def get_cancel_url(self, kwPage, req, desc):
        return '%s/member' % (kwPage['homeurl'],)

class DMActionMemberDelete(DMActionMemberPublic):
    def __init__(self, desc, params):
        DMActionMemberPublic.__init__(self, desc, params)

    def action(self, kw, req, desc):
        self.check_perm(kw)
        mobjname = DelMember(self.memobj)
        if mobjname is None:
            raise DMParamError, _('The member [%s] is in using.') % self.memobj.name
        logfmt = _('Member [%(v0)s] is removed by [%(v1)s]')
        getLogger().log_member(kw['mobj'], kw['hobj'],
                              logfmt % MkKV(mobjname, kw['mobj'].name))
        return DMAction.action(self, kw, req, desc)

class DMActionMemberDisable(DMActionMemberPublic):
    def __init__(self, desc, params):
        DMActionMemberPublic.__init__(self, desc, params)
    
    def action(self, kw, req, desc):
        self.check_perm(kw)
        self.memobj.enabled = False
        self.memobj.save()
        logfmt = _('Member [%(v0)s] is disabled by [%(v1)s]')
        getLogger().log_member(kw['mobj'], kw['hobj'],
                              logfmt % MkKV(self.memobj.name, kw['mobj'].name))
        return DMAction.action(self, kw, req, desc)

class DMActionMemberEnable(DMActionMemberPublic):
    def __init__(self, desc, params):
        DMActionMemberPublic.__init__(self, desc, params)
    
    def action(self, kw, req, desc):
        self.check_perm(kw)
        self.memobj.enabled = True
        self.memobj.save()
        logfmt = _('Member [%(v0)s] is enabled by [%(v1)s]')
        getLogger().log_member(kw['mobj'], kw['hobj'],
                              logfmt % MkKV(self.memobj.name, kw['mobj'].name))
        return DMAction.action(self, kw, req, desc)

class DMActionMemberEdit(DMActionMemberPublic):
    def __init__(self, desc, params):
        DMActionMemberPublic.__init__(self, desc, params)
        self.url_user_id = params and params[0] or None
    
    def action(self, kw, req, desc):
        if kw['mobj'].id == self.memid: memobj = kw['mobj']
        elif 'super' in kw['mobj_perms']: memobj = self.memobj
        else:
            raise DMParamError, _('Only super user and the user himself can do this.')
        mpobjs = DBMemberPrefs.objects.filter(member = memobj)
        if len(mpobjs) > 0: mpobj = mpobjs[0]
        else: mpobj = DBMemberPrefs(member = memobj, theme = 'default')
        if memobj.sourceid == DBMember.LOCAL:
            pwd = req.POST.get('EDIT_MEMBER_PWD', '')
            pwdcfm = req.POST.get('EDIT_MEMBER_PWDCFM', '')
            if pwd != '':
                if pwd != pwdcfm:
                    raise DMParamError, _('Password different with Password Confirm')
                memobj.UserAddOrEdit(pwd = pwd)
            memobj.name = req.POST.get('EDIT_MEMBER_NAME', '')
            memobj.email = req.POST.get('EDIT_MEMBER_EMAIL', '')
            memobj.mobile = req.POST.get('EDIT_MEMBER_MOBILE', '')
            memobj.save()
        elif not trial and memobj.sourceid == DBMember.SSOAUTH:
            reqmember = memobj.member
            memobj = GetSsoMember(memobj)
            if memobj is None:
                raise DMParamError, _('Get Sso info for [%s] failed.') % reqmember
            memobj.mobile = req.POST.get('EDIT_MEMBER_MOBILE', '')
            memobj.save()
        mpobj.theme = req.POST.get('EDIT_MEMBER_THEME', 'default')
        mpobj.save()
        logfmt = _('Member [%(v0)s] is edited by [%(v1)s]')
        getLogger().log_member(kw['mobj'], kw['hobj'],
                              logfmt % MkKV(memobj.name, kw['mobj'].name))
        return DMAction.action(self, kw, req, desc)

class DMActionMemberPermEdit(DMActionMemberPublic): 
    def __init__(self, desc, params):
        DMActionMemberPublic.__init__(self, desc, params)
    
    def action(self, kw, req, desc):
        if kw['mobj'].id == self.memid: memobj = kw['mobj']
        elif 'super' in kw['mobj_perms']: memobj = self.memobj
        else:
            raise DMParamError, _('Only super user and the user himself can do this.')
        pobjs = DBPerm.objects.all()
        pobjs0 = map(lambda mpobj: mpobj.perm,
                     DBMemberPerm.objects.filter(member = memobj))
        addset = []
        rmset = []
        for pobj in pobjs:
            checkval = bool(req.POST.get('PERM_CHECK_%u' % pobj.id))
            curval = pobj in pobjs0
            if checkval and not curval:
                mpobj = DBMemberPerm(member = memobj, perm = pobj)
                mpobj.save()
                addset.append(pobj.name)
            if not checkval and curval:
                DBMemberPerm.objects.filter(member = memobj, perm = pobj).delete()
                rmset.append(pobj.name)
        logfmt = _('Member [%(v0)s] is edited by [%(v1)s]: Permission [%(v2)s] added, [%(v3)s] removed.')
        getLogger().log_member(kw['mobj'], kw['hobj'],
                              logfmt % MkKV(memobj.name, kw['mobj'].name,
                                            ', '.join(addset), ', '.join(rmset)))
        return DMAction.action(self, kw, req, desc)

class DMViewPermNew(DMView):
    def __init__(self, desc, params):
        self.width = 2
        DMView.__init__(self, desc, params)
        self.template = 'view.perm.new.html'
        self.reqctx = True

    def render(self, kwPage, req, desc):
        return { 'editable': kwPage['is_super'],
                 'actionurl': '%s/perm/new' % kwPage['homeurl'] }

class DMActionPermNew(DMAction):
    def action(self, kw, req, desc):
        if not kw['is_super']:
            raise DMPermissionError, _('No permission to do this.')
        perm = req.POST.get('NEW_PERM_NAME', '')
        if DBPerm.objects.filter(name = perm).exists():
            raise DMPermissionError,\
                _('The provided permission [%s] is exists already.') % perm
        pobj = DBPerm(name = perm)
        pobj.save()
        logmsg = _('[%(v0)s] add a new permission [%(v1)s].') %\
            MkKV(kw['mobj'].name, perm)
        getLogger().log_perm(kw['mobj'], kw['hobj'], logmsg)
        return DMAction.action(self, kw, req, desc)

class DMViewPermList(DMView):
    def __init__(self, desc, params):
        self.row_width = desc.get('row_width', 5)
        self.width = self.row_width + 3
        DMView.__init__(self, desc, params)
        self.pobjs = DBPerm.objects.all().order_by('name')
        self.height = (len(self.pobjs) + self.row_width - 1) / self.row_width
        self.template = 'view.perm.list.html'

    def render(self, kwPage, req, desc):
        editable = kwPage['is_super']
        permlist = []
        for pobj in self.pobjs:
            cnt = DBMemberPerm.objects.filter(perm = pobj).count()
            perm = { 'name': pobj.name,
                     'nummembers': cnt,
                     'editurl': '%s/perm/edit/%u' % (kwPage['homeurl'], pobj.id),
                     'delurl': '%s/perm/del/%u' % (kwPage['homeurl'], pobj.id) }
            subperms = []
            for spobj in DBPermSubperm.objects.filter(perm = pobj):
                subperms.append({'name': spobj.subperm.name})
            perm['subperms0'], perm['subperms1'] = MkROW0(subperms, self.row_width)
            perm['rowspan'] = 1 + len(perm['subperms1'])
            permlist.append(perm)
        return { "editable": editable,
                 "row_width": self.row_width,
                 "permlist": permlist }

class DMViewPermEdit(DMView):
    def __init__(self, desc, params):
        DMView.__init__(self, desc, params)
        self.permid = int(params[-1])
        pobjs = DBPerm.objects.filter(id = self.permid)
        if len(pobjs) == 0:
            raise DMParamError, _('Unknown perm id: %u' % self.permid)
        self.pobj = pobjs[0]
        self.row_width = desc.get('width', 5)
        self.width = self.row_width
        self.template = 'view.subperm.html'
        self.reqctx = True

    def render(self, kwPage, req, desc):
        kwView = { 'row_width': self.row_width,
                   'editable': kwPage['is_super'],
                   'title0': _('Current SubPermissions of Permission [%s]') % self.pobj.name,
                   'title1': _('Avaiable SubPermissions of Permission [%s]') % self.pobj.name }
        if kwView['editable']:
            kwView['actionurl'] = '%s/perm/editact/%u' % (kwPage['homeurl'], self.pobj.id)
        subperms0 = []
        subperms1 = []
        pobjs0 = map(lambda psobj: psobj.subperm,
                     DBPermSubperm.objects.filter(perm = self.pobj))
        pobjs0.sort(cmp = CmpDBPerm)
        pobjs1 = DBPerm.objects.all().order_by('name')
        for pobj in pobjs1:
            pkw = { 'name': pobj.name,
                    'check': 'PERM_CHECK_%u' % pobj.id }
            if pobj in pobjs0: subperms0.append(pkw)
            else: subperms1.append(pkw)
        kwView['subperms0'] = MkROW(subperms0, self.row_width)
        kwView['subperms1'] = MkROW(subperms1, self.row_width)
        return kwView

class DMActionPermEdit(DMAction):
    def __init__(self, desc, params):
        DMAction.__init__(self, desc, params)
        self.permid = int(params[-1])
        pobjs = DBPerm.objects.filter(id = self.permid)
        if len(pobjs) == 0:
            raise DMParamError, _('Unknown perm id: %u') % self.permid
        self.pobj = pobjs[0]

    def action(self, kw, req, desc):
        if not kw['is_super']:
            raise DMPermissionError, _('No permission to do this.')
        pobjs = DBPerm.objects.all()
        pobjs0 = map(lambda psobj: psobj.subperm,
                     DBPermSubperm.objects.filter(perm = self.pobj))
        addset = []
        rmset = []
        for pobj in pobjs:
            checkval = bool(req.POST.get('PERM_CHECK_%u' % pobj.id))
            curval = pobj in pobjs0
            if checkval and not curval:
                psobj = DBPermSubperm(perm = self.pobj, subperm = pobj)
                psobj.save()
                addset.append(pobj.name)
            if not checkval and curval:
                DBPermSubperm.objects.filter(perm = self.pobj, subperm = pobj).delete()
                rmset.append(pobj.name)
        logfmt = _('Permission [%(v0)s] is edited by [%(v1)s]: Permission [%(v2)s] added, [%(v3)s] removed.')
        getLogger().log_member(kw['mobj'], kw['hobj'],
                              logfmt % MkKV(self.pobj.name, kw['mobj'].name,
                                            ', '.join(addset), ', '.join(rmset)))
        return DMAction.action(self, kw, req, desc)

class DMActionPermDel(DMAction):
    def __init__(self, desc, params):
        DMAction.__init__(self, desc, params)
        self.permid = int(params[-1])
        pobjs = DBPerm.objects.filter(id = self.permid)
        if len(pobjs) == 0:
            raise DMParamError, _('Unknown perm id: %u') % self.permid
        self.pobj = pobjs[0]

    def action(self, kw, req, desc):
        if not kw['is_super']:
            raise DMPermissionError, _('No permission to do this.')
        DBPermSubperm.objects.filter(subperm = self.pobj).delete()
        DBMemberPerm.objects.filter(perm = self.pobj).delete()
        self.pobj.delete()
        logfmt = _('Permission [%(v0)s] is deleted by [%(v1)s].')
        getLogger().log_member(kw['mobj'], kw['hobj'],
                              logfmt % MkKV(self.pobj.name, kw['mobj'].name))
        return DMAction.action(self, kw, req, desc)

class DMViewPermMembers(DMView):
    def __init__(self, desc, params):
        DMView.__init__(self, desc, params)
        self.permid = int(params[-1])
        pobjs = DBPerm.objects.filter(id = self.permid)
        if len(pobjs) == 0:
            raise DMParamError, _('Unknown perm id: %u' % self.permid)
        self.pobj = pobjs[0]
        self.row_width = desc.get('width', 6)
        self.width = self.row_width
        self.template = 'view.perm.members.html'
        self.reqctx = True

    def render(self, kwPage, req, desc):
        kwView = { 'row_width': self.row_width,
                   'editable': kwPage['is_super'],
                   'title0': _('Current Members of Permission [%s]') % self.pobj.name,
                   'title1': _('Avaiable Members of Permission [%s]') % self.pobj.name }
        if kwView['editable']:
            kwView['actionurl'] = '%s/perm/memberact/%u' % (kwPage['homeurl'], self.pobj.id)
        mobjs0 = map(lambda mpobj: mpobj.member,
                     DBMemberPerm.objects.filter(perm = self.pobj))
        mobjs0.sort(cmp = CmpDBMember)
        mobjs1 = DBMember.objects.filter(enabled = True).order_by('member')
        members0 = []
        members1 = []
        for mobj in mobjs1:
            mkw = { 'name': mobj.name,
                    'check': 'MEMBER_CHECK_%u' % mobj.id }
            if mobj in mobjs0: members0.append(mkw)
            else: members1.append(mkw)
        kwView['members0'] = MkROW(members0, self.row_width)
        kwView['members1'] = MkROW(members1, self.row_width)
        return kwView

class DMActionPermMemberEdit(DMAction):
    def __init__(self, desc, params):
        DMAction.__init__(self, desc, params)
        self.permid = int(params[-1])
        pobjs = DBPerm.objects.filter(id = self.permid)
        if len(pobjs) == 0:
            raise DMParamError, _('Unknown perm id: %u') % self.permid
        self.pobj = pobjs[0]

    def action(self, kw, req, desc):
        if not kw['is_super']:
            raise DMPermissionError, _('No permission to do this.')
        addset = []
        rmset = []
        mobjs0 = []
        for pmobj in DBMemberPerm.objects.filter(perm = self.pobj):
            mobj = pmobj.member
            mobjs0.append(mobj)
            if bool(req.POST.get('MEMBER_CHECK_%u' % mobj.id)): continue
            rmset.append(mobj.name)
            pmobj.delete()
        for mobj in DBMember.objects.filter(enabled = True):
            if mobj in mobjs0: continue
            if not bool(req.POST.get('MEMBER_CHECK_%u' % mobj.id)): continue
            addset.append(mobj.name)
            pmobj = DBMemberPerm(member = mobj, perm = self.pobj)
            pmobj.save()
        logfmt = _('Permission [%(v0)s] is added to Members [%(v1)s], and removed from [%(v2)s] by [%(v3)s].')
        getLogger().log_member(kw['mobj'], kw['hobj'],
                              logfmt % MkKV(self.pobj.name,
                                            ', '.join(addset),
                                            ', '.join(rmset),
                                            kw['mobj'].name))
        return DMAction.action(self, kw, req, desc)

from django.http import HttpResponse

def basic_challenge(realm=None):
    if realm is None:
        realm = 'Restricted Access'
    response = HttpResponse('Authorization Required',
                            content_type="text/plain")
    response['WWW-Authenticate'] = 'Basic realm="%s"' % (realm)
    response.status_code = 401
    return response

def basic_authenticate(authentication, suburl, isroot):
    (authmeth, auth) = authentication.split(' ', 1)
    if 'basic' != authmeth.lower():
        return None

    auth = auth.strip().decode('base64')
    username, password = auth.split(':', 1)

    # create http response
    realm = None
    if realm is None:
        realm = 'Restricted Access'
    resp = HttpResponse('Authorization Required',
                        content_type="text/plain")
    resp['WWW-Authenticate'] = 'Basic realm="%s"' % (realm)
    mobj = DBMember.objects.filter(member = username)
    if not mobj:
        resp.status_code = 401
        print('Can not find username "%s"' % username)
        return resp
    mobj = mobj[0]
    # check passwd
    if str(mobj.getPasswd()).upper() != md5(password).hexdigest().upper():
        resp.status_code = 401
        print('invalid password for "%s"' % username)
        return resp
    # check perm
    if isroot:
        resp.status_code = 200
        resp['X-Username'] = username
    elif mobj.checkSubsysPerm(suburl):
        resp.status_code = 200
        resp['X-Username'] = username
    else:
        print('"%s" has no permission "%s"' % (username, suburl))
        resp.status_code = 401
    return resp

def DMAuthView(request):
    auth = request.META.get('HTTP_AUTHORIZATION', '')

    print request.META.get('X-Real-IP', None)
    orig_uri = request.META.get('X-Origin-URI', None)
    print 'orig_uri %s' % orig_uri
    script_name = request.META.get('SCRIPT_NAME', None)
    print 'script_name %s' % script_name
    isroot = False
    if orig_uri.startswith('/devman'):
        isroot = True
        suburl = orig_uri[len('/devman'):].strip('/').split('/')
        if suburl: suburl = suburl[0]
    for prefix in ('/dmprojs', ):
        suburl = orig_uri[len(prefix):].strip('/')
    if auth:
        resp = basic_authenticate(auth, suburl, isroot)
        if resp is not None:
            #successfully authenticated
            return resp
        else:
            return basic_challenge()

    # nothing matched, still return basic challange
    return basic_challenge()

