#!/usr/bin/python
from devman.dmroot import _
from devman.dmroot.models import DBEntity, DBAttrPositiveInteger, DBAttrString
from devman.dmroot.entity import DMEntityBase, GetSysList
from devman.dmroot.period import DMPeriodWeekly

class DMLog(DMEntityBase):
    ATTRS = ({ 'klass': DBAttrPositiveInteger },
             { 'klass': DBAttrString })

    AABILL = 0
    RANDOM = 1
    MEMBER = 2
    SUBSYS = 3
    PERM   = 4
    PROJ   = 5
    Task   = 6
    LTIDALL = ((_('AABill'),),
               (_('Random'),),
               (_('Member'),),
               (_('Subsys'),),
               (_('Permission'),),
               (_('Project'),),
               (_('Task'),))

    def new(self, mobj, hobj, logtypeid, desc, parent = None):
        DMLog.__base__.new(self, mobj, parent, hobj, logtypeid, desc)
        self.logtypeid = logtypeid
        self.desc = desc

    def load(self, eobj):
        vlist = DMLog.__base__.load(self, eobj)
        self.logtypeid = vlist.pop(0)
        self.desc = vlist.pop(0)
        return vlist

    def render(self, data = None):
        kw = DMLog.__base__.render(self, data)
        kw['type'] = self.LTIDALL[self.logtypeid][0]
        kw['desc'] = self.desc
        return kw

class DMLogList(DMEntityBase):
    SubEntityKlasses = (DMLog,)

    def __init__(self):
        DMLogList.__base__.__init__(self)
        self.eobj = GetSysList('log')

    def log_aabill(self, mobj, hobj, desc):
        DMLog().new(mobj, hobj, DMLog.AABILL, desc, self)

    def log_random(self, mobj, hobj, desc):
        DMLog().new(mobj, hobj, DMLog.RANDOM, desc, self)

    def log_member(self, mobj, hobj, desc):
        DMLog().new(mobj, hobj, DMLog.MEMBER, desc, self)

    def log_perm(self, mobj, hobj, desc):
        DMLog().new(mobj, hobj, DMLog.PERM, desc, self)

    def log_subsys(self, mobj, hobj, desc):
        DMLog().new(mobj, hobj, DMLog.SUBSYS, desc, self)

    def log_proj(self, mobj, hobj, desc):
        DMLog().new(mobj, hobj, DMLog.PROJ, desc, self)
       
    def log_task(self, mobj, hobj, desc):
        DMLog().new(mobj, hobj, DMLog.Task, desc, self) 
        
SysLogList = DMLogList()
