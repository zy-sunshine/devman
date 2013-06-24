#!/usr/bin/python
from devman.dmroot import _, J_, MkKV, MkROW
from devman.dmroot.exceptions import DMPermissionError, DMParamError
from devman.dmroot.view import DMView, DMViewConfirm, DMAction
from devman.dmroot.log import SysLogList

from devman.dmsubsys.models import DBSubsys
from devman.dmproj.models import DBProject

def _get_subsys_():
    projs = []
    for subsys in DBSubsys.objects.all():
        if subsys.relpath not in projs:
            projs.append(subsys.relpath)
    return projs

def _get_proj_link(rooturl, homeurl, name):
    repourl = rooturl
    if rooturl[-3:] == '/ns': repourl = rooturl[:-3]
    proj = { 'name': name, 
             'oldtracurl': '%s/dmprojs/trac/%s' % (repourl, name),
             'newtracurl': '%s/wiki/view?project=%s;index=%s' % (homeurl, name, 'WikiStart'),
             'giturl': '%s/dmprojs/git/%s' % (repourl, name),
             'svnurl': '%s/dmprojs/svn/%s' % (repourl, name)
           }
    if homeurl[-9:] != '/devman':
        proj['delurl'] = '%s/proj/delcfm/%s' % (homeurl, name)
    return proj

def getProjs(kwPage):
    projs = []
    if kwPage['homeurl'][-9:] == '/devman':
        for subsys in _get_subsys_():
            projs.append({'name': subsys})
    else:
        for dbproj in DBProject.objects.filter(home=kwPage['hobj']):
            projs.append({'name': dbproj.name})
    return projs

def getProjLinks(kwPage):
    projs = []
    if kwPage['homeurl'][-9:] == '/devman':
        for subsys in _get_subsys_():
            projs.append(_get_proj_link(kwPage['rooturl'], kwPage['homeurl'], subsys))
    else:
        for pobj in DBProject.objects.filter(home=kwPage['hobj']):
            projs.append(_get_proj_link(kwPage['rooturl'], kwPage['homeurl'], pobj.name))
    return projs

class DMViewProjectList(DMView):
    def __init__(self, desc, params):
        DMView.__init__(self, desc, params)
        self.width = 6
        self.template = 'view.proj.list.html'

    def render(self, kwPage, req, desc):
        projs = getProjLinks(kwPage)
        return { 'projs': projs }

class DMViewProjectTableList(DMView):
    def __init__(self, descTaskView, params):
        DMView.__init__(self, descTaskView, params)
        self.width = 10
        self.reqctx = True
        self.template = 'view.task.projectlist.html'
        
    def render(self, kwPage, req, descTaskView):
	proj = req.GET.get('project', '')
	title = descTaskView.get('title', '')
        projs = getProjs(kwPage)
        return {'title': J_(title), 'projects': MkROW(projs, self.width), 'proj': proj}
	

class DMViewProjectNew(DMView):
    def __init__(self, desc, params):
        DMView.__init__(self, desc, params)
        self.reqctx = True
        self.width = 4
        self.template = 'view.proj.new.html'

    def validate(self, kwPage, req, desc):
        return kwPage['is_super']

class DMActionProjectNew(DMAction):
    def is_valid_project_name(self, name):
        testname = name
        for ch in '_-.': testname = testname.replace(ch, '0')
        return testname.isalnum()

    def action(self, kw, req, desc):
        if not kw['is_super']:
            raise DMPermissionError, _('Only super user can do this operation.')
        name = req.POST.get('NEW_PROJ_NAME', '')
        if name == '':
            raise DMParamError, _('Project name is not provided.')
        if not self.is_valid_project_name(name):
            raise DMParamError, _('Invalid project name, must be "[0-9A-Za-z\.\-\_]+"')
        if DBProject.objects.filter(home=kw['hobj'],name = name).exists():
            raise DMParamError, _('Project %s exists already.') % repr(name)
        pobj = DBProject(home=kw['hobj'],name = name)
        pobj.save()
        logfmt = _('Project [%(v0)s] is created by [%(v1)s].')
        SysLogList.log_proj(kw['mobj'], kw['hobj'],
                            logfmt % MkKV(pobj.name, kw['mobj'].name))
        return DMAction.action(self, kw, req, desc)

class DMActionProjectPublic(DMAction):
    def __init__(self, desc, params):
        DMAction.__init__(self, desc, params)
        self.projname = params[-1]

    def check_perm(self, kw):
        if not kw['is_super']:
            raise DMPermissionError, _('Only super user can do this operation.')
            
    def get_proj(self, kw):
        pobjs = DBProject.objects.filter(home=kw['hobj'],name = self.projname)
        if len(pobjs) == 0:
            raise DMParamError, _('Project %s not found.') % self.projname
        return pobjs[0]

class DMActionProjectEdit(DMActionProjectPublic):
    def __init__(self, desc, params):
        DMActionProjectPublic.__init__(self, desc, params)

    def action(self, kw, req, desc):
        self.check_perm(kw)
        pobj = self.get_proj(kw)
        pobj.save()
        logfmt = _('Project [%(v0)s] is edited by [%(v1)s].')
        SysLogList.log_proj(kw['mobj'], kw['hobj'],
                            logfmt % MkKV(pobj.name, kw['mobj'].name))
        return DMAction.action(self, kw, req, desc)

class DMViewProjectDeleteConfirm(DMViewConfirm):
    def __init__(self, desc, params):
        DMViewConfirm.__init__(self, desc, params)
        self.projname = params[-1]

    def get_prompt(self, kwPage, req, desc):
        return _('Do you really want to delete "%s"?') % self.projname

    def get_confirm_url(self, kwPage, req, desc):
        return '%s/proj/del/%s' % (kwPage['homeurl'], self.projname)

    def get_cancel_url(self, kwPage, req, desc):
        return kwPage['homeurl']

# class DMViewProjectPublic(DMView):
#     def __init__(self, desc, params):
#         DMView.__init__(self, desc, params)
#         if len(params) < 1:
#             raise DMParamError, _('The required project name is missed.')
#         projname = params[-1]
#         pobjs = DBProject.objects.filter(home=kwPage['hobj'],name = projname)
#         if len(pobjs) == 0:
#             raise DMParamError, _('Invalid project name %s.') % projname
#         self.pobj = pobjs[0]

class DMActionProjectDelete(DMActionProjectPublic):
    def action(self, kw, req, desc):
        self.check_perm(kw)
        pobj = self.get_proj(kw)
        logfmt = _('Project [%(v0)s] is removed by [%(v1)s].')
        SysLogList.log_proj(kw['mobj'], kw['hobj'],
                            logfmt % MkKV(pobj.name, kw['mobj'].name))
        DBProject.objects.filter(home=kw['hobj'], name = pobj.name).delete()
        return DMAction.action(self, kw, req, desc)

