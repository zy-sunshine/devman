#!/usr/bin/python
from datetime import datetime, timedelta
from devman.settings import entityroot_id, topsyslists
from devman.dmroot import _, timefmt, datetimefmt, datestart, MkKV
from devman.dmroot.exceptions import DMIDError, DMEntityError
import devman.dmroot.period as PeriodModule
from devman.dmroot.models import DBMember, DBEntity, DBAttrPositiveInteger,\
    DBAttrInteger, DBAttrString, DBAttrDateTime, DBAttrMember,\
    DBCommentText, DBCommentCachedText

def RecurDeleteEntity(eobj):
    subeobjs = DBEntity.objects.filter(parent = eobj.id)
    for subeobj in subeobjs: RecurDeleteEntity(subeobj)
    DBAttrPositiveInteger.objects.filter(entity = eobj).delete()
    DBAttrInteger.objects.filter(entity = eobj).delete()
    DBAttrString.objects.filter(entity = eobj).delete()
    DBAttrDateTime.objects.filter(entity = eobj).delete()
    DBAttrMember.objects.filter(entity = eobj).delete()
    DBCommentText.objects.filter(entity = eobj).delete()
    DBCommentCachedText.objects.filter(entity = eobj).delete()
    eobj.delete()

class DMEntityBase(object):
    def __init__(self):
        self.attrs = []
        klass = self.__class__
        while klass != DMEntityBase:
            if hasattr(klass, 'ATTRS'):
                self.attrs = list(klass.ATTRS) + self.attrs
            klass = klass.__base__

    def get_subentity(self, eobj):
        if self.eobj.id != eobj.parent:
            raise DMEntityError,\
                _('%(v0)u is not the parent of %(v1)u') % MkKV(self.eobj.id, eobj.id)
        klass = self.__class__
        if not hasattr(klass, 'SubEntityKlasses'):
            raise DMEntityError,\
                _('SubEntityKlasses is not defined for %s.') % repr(klass.__name__)
        for subklass in klass.SubEntityKlasses:
            if eobj.klass != subklass.__name__: continue
            obj = subklass()
            obj.load(eobj)
            return obj
        raise DMEntityError, _('%s is not allowed.') % repr(eobj.klass)

    def get_subentity_byid(self, eid):
        eobjs = DBEntity.objects.filter(id = eid)
        if len(eobjs) == 0:
            raise DMEntityError, _('Invalid entity id %u') % eid
        return self.get_subentity(eobjs[0])

    def get_attridx(self, klass, idx):
        while klass != DMEntityBase:
            if hasattr(klass, 'ATTRS'): idx = idx + len(klass.ATTRS)
            klass = klass.__base__
        return idx

    def set_attr(self, klass, idx, value):
        attr = self.get_attridx(klass, idx)
        klass = self.attrs[attr]['klass']
        klass.objects.filter(entity = self.eobj, attr = attr).delete()
        aobj = klass(entity = self.eobj, attr = attr, value = value)
        aobj.save()

    def new(self, mobj, parent = None, hobj = None, *values):
        now = datetime.now()
        self.eobj = DBEntity(parent = parent.eobj.id,
                             klass = self.__class__.__name__,
                             owner = mobj,
                             home = hobj,
                             create_date = now,
                             lastedit_date = now)
        self.eobj.save()
        for attr in range(len(self.attrs)):
            klass = self.attrs[attr]['klass']
            vobj = klass(entity = self.eobj, attr = attr, value = values[attr])
            vobj.save()
        # Override by subclass.

    def new_byreq(self, req, mobj, parent = None, hobj = None):
        values = []
        for attr in range(len(self.attrs)):
            attrtype = self.attrs[attr]['type']
            attrpost = self.attrs[attr]['post']
            values.append(attrtype(req.POST.get(attrpost)))
        return self.new(mobj, parent, hobj, *values)

    def load(self, eobj):
        self.eobj = eobj
        vlist = []
        for attr in range(len(self.attrs)):
            klass = self.attrs[attr]['klass']
            vobjs = klass.objects.filter(entity = self.eobj, attr = attr)
            if len(vobjs) == 0: vlist.append(None)
            else: vlist.append(vobjs[0].value)
        return vlist
        # Override by subclass.

    def load_byid(self, eid):
        eobjs = DBEntity.objects.filter(id = eid)
        if len(eobjs) == 0: raise DMIDError, _('The id %u not found.') % eid
        return self.load(eobjs[0])

    def update_byreq(self, req, mobj):
        self.eobj.lastedit_date = datetime.now()
        self.eobj.save()
        # Override by subclass.

    def render(self, data = None):
        # Override by subclass.
        if DBMember.objects.filter(id = self.eobj.owner_id).exists():
            ownername = self.eobj.owner.name
        else:
            ownername = 'user id: #%u' % self.eobj.owner_id
        return { 'owner': ownername,
                 'create_date': self.eobj.create_date.strftime(datetimefmt),
                 'create_time': self.eobj.create_date.strftime(timefmt),
                 'lastedit_date': self.eobj.lastedit_date.strftime(datetimefmt),
                 'lastedit_time': self.eobj.lastedit_date.strftime(timefmt) }

    def get_period(self, desc):
        klass = PeriodModule.__dict__[desc.get('period', 'DMPeriodForever')]
        return klass(self.eobj, desc)

    def render_urls(self, homeurl, desc):
        period = self.get_period(desc)
        start = period.getstart(datestart)
        kwlist = []
        while start <= datetime.now():
            fkw = period.get_filter(start)
            if DBEntity.objects.filter(**fkw).exists():
                kwlist.append({ 'url': period.url(homeurl, start),
                                'prompt': period.prompt(start) })
            start = period.getend(start)
        if period.order[0] == '-': kwlist.reverse()
        return kwlist

    def render_subs(self, desc = {}, curdate = None, hobj = None, data = None):
        period = self.get_period(desc)
        fkw = period.get_filter(curdate)
        if hobj is not None: fkw['home'] = hobj
        kwlist = []
        for eobj in DBEntity.objects.filter(**fkw).order_by(period.order):
            subobj = self.get_subentity(eobj)
            kwlist.append(subobj.render(data))
        return kwlist

    def render_subs_insteps(self, desc, curdate, hobj = None, data = None):
        period = self.get_period(desc)
        start = period.getstart(curdate)
        end = period.getend(start)
        kwlist = []
        curstart = start
        while curstart < end:
            curend = curstart + period.getstep(curstart)
            fkw = period._get_filter(curstart, curend)
            if hobj is not None: fkw['home'] = hobj
            eobjs = DBEntity.objects.filter(**fkw).order_by(period.order)
            ekws = []
            for eobj in eobjs:
                subobj = self.get_subentity(eobj)
                ekws.append(subobj.render(data))
            if ekws:
                kwlist.append({ 'prompt': period.step_prompt(curstart),
                                'entities': ekws })
            curstart = curend
        if period.order[0] == '-': kwlist.reverse()
        return kwlist

def EntityCheckMember(mobj):
    if DBEntity.objects.filter(owner = mobj).exists(): return True
    if DBAttrMember.objects.filter(value = mobj).exists(): return True
    return False

SysList_eobjs = DBEntity.objects.filter(parent = entityroot_id).order_by('id')

def GetSysList(name):
    return SysList_eobjs[topsyslists.index(name)]
