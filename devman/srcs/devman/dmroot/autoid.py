#!/usr/bin/python
from devman.dmroot.models import DBIDValue, DBIDScope, DBMember

class AutoID(object):
    def __init__(self, idtypeid):
        self.idtypeid = idtypeid

    def request(self):
        iobjs = DBIDValue.objects.filter(idtypeid = self.idtypeid)
        if len(iobjs) > 0:
            value = iobjs[0].val
            iobjs[0].delete()
            return value
        iobjs = DBIDScope.objects.filter(idtypeid = self.idtypeid)
        if len(iobjs) == 0: return None
        value = iobjs[0].minval
        iobjs[0].minval = value + 1
        if iobjs[0].minval == iobjs[0].maxval: iobjs[0].delete()
        else: iobjs[0].save()
        return value

    def restore(self, value):
        iobjs = DBIDValue.objects.filter(idtypeid = self.idtypeid, val = value)
        if len(iobjs) > 0: return
        iobj = DBIDValue(idtypeid = self.idtypeid, val = value)
        iobj.save()

AutoLocalUID = AutoID(DBMember.LOCAL)