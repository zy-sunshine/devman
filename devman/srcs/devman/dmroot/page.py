#!/usr/bin/python
import json, os.path
from datetime import datetime
from django import VERSION as django_version
from django.template import RequestContext
from django.shortcuts import render_to_response
from devman.settings import workdir, selfver, trial, logresp
from devman.dmroot import _, J_, datetimefmt, MkKV
from devman.dmroot.models import DBMember, DBMemberPrefs
from devman.dmroot.urlconf import DMUrlConf
from devman.dmroot.exceptions import DMJsonDescError,\
    DMNotLoginError, DMInvalidUserError, DMPermissionError

class DMPage(object):
    def __init__(self, req, getviewobj, getactionobj):
        self.getviewobj = getviewobj
        self.getactionobj = getactionobj
        self.mobj = None
        self.reqctx = True
        if req.is_secure(): protocol = 'https'
        else: protocol = 'http'
        self.rooturl = '%s://%s%s' % (protocol, req.get_host(), req.path[:-len(req.path)])
        self.cururl = req.path
        
        fp = _(u'Powered by devman-%(v0)u(django-%(v1)u.%(v2)u.%(v3)u)') %\
            MkKV(selfver, *django_version[:3])
        self.kw = { 'failed': None,
                    'trial': trial,
                    'title': _('devman exception'),
                    'mobj_prompt': _('Not login yet'),
                    'mobj_url': self.rooturl + '/login',
                    'footprint': fp,
                    'barlinks': [],
                    'filters': [],
                    'rooturl': self.rooturl,
                    'cururl': self.cururl,
                    'host': req.get_host(),
                    'curtime': datetime.now().strftime(datetimefmt),
                    'curpath': req.path,
                    'themecss': self.rooturl + '/incs/theme.default.css',
                    'wikicss': self.rooturl + '/incs/theme.wiki.css',
                    'datecss': self.rooturl + '/incs/date.css',
                    'datejs': self.rooturl + '/incs/date.js',
                    'ajaxjs': self.rooturl + '/incs/ajax.js',
                    'chartcss': self.rooturl + '/incs/chart.css',
                    'chartjs': self.rooturl + '/incs/chart.js',
                    'logout': self.rooturl + '/login' }

    def loadmobj(self, req):
        if isinstance(self.mobj, DBMember): return
        if trial:
            if req.POST.has_key('loginname'):
                req.COOKIES['loginname'] = req.POST.get('loginname')
            member = req.COOKIES.get('loginname', None)
        else:
            member = req.environ.get('REMOTE_USER', None)
        if member is None:
            if trial: self.kw['tourl'] = '%s/login' % self.rooturl
            raise DMNotLoginError, 'Not login yet.'
        mobjs = DBMember.objects.filter(member = member)
        if len(mobjs) == 0:
            raise DMInvalidUserError, 'Invalid user %s.' % repr(member)
        self.mobj = mobjs[0]
        self.mobj.lastlogin = datetime.now()
        self.mobj.save()
        self.kw['mobj'] = self.mobj
        self.kw['mobj_prompt'] = _('Login as %s') %\
            ('%s(%s)' % (self.mobj.name, member))
        self.kw['mobj_perms'] = self.mobj.getperms()
        self.kw['mobj_url'] = '%s/dmroot/member/view/%u' % (self.rooturl, self.mobj.id)
        self.kw['is_super'] = 'super' in self.kw['mobj_perms']
        mpobjs = DBMemberPrefs.objects.filter(member = self.mobj)
        if len(mpobjs) == 0:
            self.kw['mobj_theme'] = 'default'
        else:
            self.kw['mobj_theme'] = mpobjs[0].theme
        self.kw['themecss'] = '%s/incs/theme.%s.css' %\
            (self.rooturl, self.kw['mobj_theme'])
        if not self.kw['urlconf'].check_perm(self.mobj):
            raise DMPermissionError, _('Access here is not permitted.')

    def loadview(self, align, descView, req, params):
        if 'name' in descView and descView['name'] in self.named_views:
            viewobj = self.named_views[descView['name']]
        else:
            viewobj = self.getviewobj(descView, params)
            if self.mobj is None and viewobj.needmobj: self.loadmobj(req)
            if 'name' in descView: self.named_views[descView['name']] = viewobj
        if not viewobj.validate(self.kw, req, descView): return []
        kwView = viewobj.render(self.kw, req, descView)
        kwView['template'] = viewobj.template
        kwView['align'] = align
        kwView['width'] = viewobj.width
        kwView['twidth'] = descView.get('twidth', '100%')
        kwView['width_1'] = viewobj.width - 1
        if not self.reqctx: self.reqctx = viewobj.reqctx
        return [kwView]

    def loadjson(self, req):
        project = req.GET.get('project', '')
        wikiname =  req.GET.get('index', '')
        ucobj = DMUrlConf(self.cururl)
        #ucobj = DMUrlConf(req.path)
        descPage = ucobj.descs
        self.homeurl = ucobj.get_homeurl(self.rooturl)
        self.kw['homeurl'] = self.homeurl
        self.fromurl = self.homeurl
        if 'HTTP_REFERER' in req.META: self.fromurl = req.META['HTTP_REFERER']
        self.kw['fromurl'] = self.fromurl
        self.kw['project'] = project
        self.kw['urlconf'] = ucobj
        self.kw['hobj'] = ucobj.get_dbhomeobj()
      
        if req.path_info != '/login':
            self.kw['logout']= { 'prompt': _('Logout'),
                                 'urlpath': self.kw['logout'] }
        if 'title' in descPage: self.kw['title'] = J_(descPage['title'])
        if "action" in descPage:
            if self.mobj is None: self.loadmobj(req)
            actionobj = self.getactionobj(descPage['action'], ucobj.params)
            actionurl = actionobj.action(self.kw, req, descPage['action'])
            self.kw['tourl'] = actionurl
            if project != '' and actionurl.index('project=')==-1:
                self.kw['tourl'] = '%s?project=%s' % (actionurl, project)
            return
        for bl in descPage.get('barlinks', []):
            blkw = { 'prompt': J_(bl[0]),
                     'urlpath': bl[1] % { 'homeurl': self.kw['homeurl'], 'project': 'devman' } }
            self.kw['barlinks'].append(blkw)
        self.kw['seclinks'] = []
        for sl in descPage.get('seclinks', []):
            slkw = { 'prompt': J_(sl[0]),
                     'urlpath': sl[1] % { 'homeurl': self.kw['homeurl'], 'wikistart': 'WikiStart', 'wikiname': wikiname, 'project': 'devman' } }
            self.kw['seclinks'].append(slkw)
        self.kw['tiplinks'] = []
        for tl in descPage.get('tiplinks', []):
            olkw = { 'prompt': J_(tl[0]),
                     'urlpath': tl[1] % { 'homeurl': self.kw['homeurl'], 'project': project, 'backurl': self.kw['fromurl'], \
                                          'wikistart': 'WikiStart', 'wikiname': wikiname} }
            self.kw['tiplinks'].append(olkw)
        if "search" in descPage:
            urlpath = descPage["search"]['urlpath'] % { 'homeurl': self.kw['homeurl'], 'project': project }
            self.kw['filters'] = {'urlpath':urlpath, 'items': descPage["search"]['items']}

        self.kw['viewrows'] = []
        self.named_views = {}
        for descViewRow in descPage['viewrows']:
            kwViewRow = []
            if isinstance(descViewRow, list):
                for descView in descViewRow:
                    align = descView.get('align', 'center')
                    kwViewRow.extend(self.loadview(align, descView, req, ucobj.params))
            elif isinstance(descViewRow, dict):
                for align in ('left', 'center', 'right'):
                    if align not in descViewRow: continue
                    kwViewRow.extend(self.loadview(align, descViewRow[align], req, ucobj.params))
            else:
                raise DMJsonDescError, _('descViewRow must be list or dict.')
            if kwViewRow: self.kw['viewrows'].append(kwViewRow)

    def response(self, req):
        reqkw = {}
        if self.reqctx: reqkw['context_instance'] = RequestContext(req)
        response = render_to_response('frame.html', self.kw, **reqkw)
        if trial and req.COOKIES.has_key('loginname'):
            response.set_cookie('loginname', req.COOKIES.get('loginname'))
        if req.path_info == '/login' and req.COOKIES.has_key('loginname'):
            response.delete_cookie('loginname')
        if logresp:
            nowstr = datetime.now().strftime('%Y%m%d-%H%M%S')
            cnt = 0
            while True:
                logfn = os.path.join(workdir, 'resp-%s-%u.log' % (nowstr, cnt))
                if not os.path.exists(logfn): break
                cnt = cnt + 1
            logfp = open(logfn, 'wt')
            logfp.write('---- %s(%s) ----\n' % (req.path_info, nowstr))
            logfp.write(response.content)
            logfp.close()
        return response

    def set_failed(self, message):
        self.kw['failed'] = message
        self.kw['barlinks'] = []
        self.kw['seclinks'] = []
        if trial: return
        self.kw['mobj_url'] = None
