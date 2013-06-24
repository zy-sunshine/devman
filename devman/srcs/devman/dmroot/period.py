#!/usr/bin/python
from datetime import datetime, timedelta
from devman.dmroot import _, monthfmt, datefmt

class DMPeriod(object):
    def __init__(self, eobj, desc):
        self.eobj = eobj
        self.urlfmt = desc.get('urlfmt', '%(homeurl)s')
        self.order = desc.get('order', '-lastedit_date')
        order_col = self.order
        if order_col[0] == '-': order_col = order_col[1:]
        self.date_gte = '%s__gte' % order_col
        self.date_lt = '%s__lt' % order_col

    def _get_filter(self, start, end):
        return { 'parent': self.eobj.id,
                 self.date_gte: start,
                 self.date_lt: end }

    def get_filter(self, dtobj = None):
        if dtobj is None: return { 'parent': self.eobj.id }
        return self._get_filter(self.getstart(dtobj), self.getend(dtobj))

class DMPeriodForever(DMPeriod):
    def url(self, homeurl, dtobj):
        return self.urlfmt % { 'homeurl': homeurl,
                               'datetime': 'null' }

    def get_filter(self, dtobj):
        return { 'parent': self.eobj.id }

    def step_prompt(self, start):
        return start.strftime(datefmt)

    def getstart(self, dtobj):
        return datestart

    def getend(self, dtobj):
        return datetime.now()

    def getstep(self, start):
        return timedelta(days = 1)

class DMPeriodDaily(DMPeriod):
    def url(self, homeurl, dtobj):
        return self.urlfmt % { 'homeurl': homeurl,
                               'datetime': dtobj.strftime(datefmt) }

    def prompt(self, start):
        return start.strftime(datefmt)

    def step_prompt(self, start):
        return start.strftime(datefmt)

    def getstart(self, dtobj):
        return datetime.strptime(dtobj.strftime(datefmt), datefmt)

    def getend(self, start):
        return start + timedelta(days = 1)

    def getstep(self, start):
        return timedelta(days = 1)

weeknames = (_(u'Monday'), _(u'Tuesday'), _(u'Wednesday'), _(u'Thursday'),
             _(u'Friday'), _(u'Saturday'), _(u'Sunday'))
class DMPeriodWeekly(DMPeriod):
    def url(self, homeurl, dtobj):
        return self.urlfmt % { 'homeurl': homeurl,
                               'datetime': dtobj.strftime(datefmt) }

    def prompt(self, start):
        return u'%s/%s' % (start.strftime(datefmt),
                          (start + timedelta(days = 6)).strftime(datefmt))

    def step_prompt(self, start):
        weekname = weeknames[start.weekday()]
        return u'%s(%s)' % (start.strftime(datefmt), weekname)

    def getstart(self, dtobj):
        dtobj = dtobj - timedelta(days = dtobj.weekday())
        return datetime.strptime(dtobj.strftime(datefmt), datefmt)

    def getend(self, start):
        return start + timedelta(days = 7)

    def getstep(self, start):
        return timedelta(days = 1)

monthnames = (_(u'January'), _(u'February'), _(u'March'), _(u'April'),
              _(u'May'), _(u'June'), _(u'July'), _(u'August'),
              _(u'September'), _(u'October'), _(u'November'), _(u'December'))
class DMPeriodMonthly(DMPeriod):
    def url(self, homeurl, dtobj):
        return self.urlfmt % { 'homeurl': homeurl,
                               'datetime': dtobj.strftime(monthfmt) }

    def prompt(self, start):
        return start.strftime(monthfmt)

    def step_prompt(self, start):
        return start.strftime(datefmt)

    def getstart(self, dtobj):
        return datetime.strptime(dtobj.strftime(monthfmt), monthfmt)

    def getend(self, start):
        numdays = 32 - (start + timedelta(days = 31)).day
        return start + timedelta(days = numdays)

    def getstep(self, start):
        return timedelta(days = 1)
