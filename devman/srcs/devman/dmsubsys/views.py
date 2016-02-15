#!/usr/bin/python
from devman.dmroot import _, MkROW, MkROW0, MkKV
from devman.dmroot.models import CmpDBMember
from devman.dmroot.view import DMView, DMAction
from devman.dmroot.log import getLogger
from devman.dmsubsys.models import DBSubsys, DBSubsysMember,\
    CmpDBSubsysMember, UpdateSsoRecords
from devman.dmsubsys.subsys import DMSubsysObject
from devman.dmroot.exceptions import DMParamError

class DMViewSubsysList(DMView):
    def __init__(self, desc, params):
        DMView.__init__(self, desc, params)
        self.row_width = desc.get('width', 5)
        self.width = 1 + self.row_width + 1
        self.template = 'view.subsys.list.html'
        self.sstype = desc.get('sstype', 'trac')

    def render(self, kwPage, req, desc):
        subsyses = []
        for ssobj in DBSubsys.objects.filter(sstype = self.sstype).order_by('relpath'):
            subsysobj = DMSubsysObject(ssobj, desc)
            sskw = { 'link': subsysobj.getlink(kwPage),
                     'linkname': subsysobj.getlinkname(kwPage) }
            smobjs = list(DBSubsysMember.objects.filter(subsys = ssobj))
            smobjs.sort(cmp = CmpDBSubsysMember)
            sses = []
            for smobj in smobjs:
                if not smobj.member.enabled: continue
                if smobj.ipaddr is None or smobj.ipaddr == '': name = smobj.member.name
                else: name = '%s(%s)' % (smobj.member.name, smobj.ipaddr)
                sses.append({ 'name': name })
            sskw['members0'], sskw['members1'] = MkROW0(sses, self.row_width)
            sskw['rowspan'] = len(sskw['members1']) + 1
            if kwPage['is_super']:
                sskw['editurl'] =\
                        '%s/edit/%u' % (kwPage['homeurl'], ssobj.id)
            subsyses.append(sskw)
        return { 'row_width': self.row_width,
                 'title': '[%s]' % self.sstype,
                 'subsyses': subsyses }

class DMViewSubsysEdit(DMView):
    def __init__(self, desc, params):
        DMView.__init__(self, desc, params)
        subsysid = int(params[-1])
        subsysobjs = DBSubsys.objects.filter(id = subsysid)
        if len(subsysobjs) == 0:
            raise DMParamError, _('Unknown subsys id: %u') % subsysid
        self.ssobj = subsysobjs[0]
        self.width = desc.get('width', 5)
        self.template = 'view.subsys.edit.html'
        self.reqctx = True

    def validate(self, kwPage, req, desc):
        return kwPage['is_super']

    def render(self, kwPage, req, desc):
        mobjs0 = map(lambda smobj: smobj.member,
                     DBSubsysMember.objects.filter(subsys = self.ssobj))
        mobjs1 = DMSubsysObject(self.ssobj, desc).permitted_members()
        mobjs0.sort(cmp = CmpDBMember)
        mobjs1.sort(cmp = CmpDBMember)
        members0 = []
        members1 = []
        for mobj in mobjs1:
            mkw = { 'check': 'SUBSYS_MEMBER_%u' % mobj.id,
                    'name': mobj.name }
            if mobj in mobjs0: members0.append(mkw)
            else: members1.append(mkw)
        return { 'title': _('Edit members of %(v0)s[%(v1)s]') %\
                     MkKV(self.ssobj.relpath, self.ssobj.sstype),
                 'actionurl': '%s/editact/%u' %\
                     (kwPage['homeurl'], self.ssobj.id),
                 'members0': MkROW(members0, self.width),
                 'members1': MkROW(members1, self.width) }

class DMActionSubsysEdit(DMAction):
    def __init__(self, desc, params):
        DMAction.__init__(self, desc, params)
        subsysid = int(params[-1])
        subsysobjs = DBSubsys.objects.filter(id = subsysid)
        if len(subsysobjs) == 0:
            raise DMParamError, _('Unknown subsys id: %u') % subsysid
        self.ssobj = subsysobjs[0]

    def action(self, kw, req, desc):
        mobjs0 = map(lambda smobj: smobj.member,
                     DBSubsysMember.objects.filter(subsys = self.ssobj))
        mobjs1 = DMSubsysObject(self.ssobj, desc).permitted_members()
        addset = []
        rmset = []
        for mobj in mobjs1:
            checkval = bool(req.POST.get('SUBSYS_MEMBER_%u' % mobj.id))
            curval = mobj in mobjs0
            if checkval and not curval:
                smobj = DBSubsysMember(subsys = self.ssobj, member = mobj)
                smobj.save()
                addset.append(mobj)
            if not checkval and curval:
                DBSubsysMember.objects.filter(subsys = self.ssobj, member = mobj).delete()
                rmset.append(mobj)
        UpdateSsoRecords(self.ssobj, addset, rmset)
        logfmt = _('Subsys [%(v0)s[%(v1)s]] is edited by [%(v2)s]: Member [%(v3)s] added, [%(v4)s] removed.')
        getLogger().log_subsys(kw['mobj'], kw['hobj'],
                              logfmt % MkKV(self.ssobj.relpath,
                                            self.ssobj.sstype,
                                            kw['mobj'].name,
                                            ', '.join(map(lambda add: add.name, addset)),
                                            ', '.join(map(lambda rm: rm.name, rmset))))
        return DMAction.action(self, kw, req, desc)
