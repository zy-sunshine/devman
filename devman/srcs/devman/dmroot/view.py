#!/usr/bin/python

class DMView(object):
    def __init__(self, desc, params):
        self.params = params
        self.template = None
        self.reqctx = False
        self.needmobj = True

    def validate(self, kw, req, desc):
        return True

    def render(self, kwPage, req, desc):
        return {}

class DMViewConfirm(DMView):
    def __init__(self, desc, params):
        DMView.__init__(self, desc, params)
        self.width = 2
        self.template = 'view.confirm.html'

    def render(self, kwPage, req, desc):
        return { 'prompt': self.get_prompt(kwPage, req, desc),
                 'confirm_url': self.get_confirm_url(kwPage, req, desc),
                 'cancel_url': self.get_cancel_url(kwPage, req, desc) }

class DMAction(object):
    def __init__(self, desc, params):
        self.params = params

    def action(self, kw, req, desc): # virtual func.
        tourl = req.POST.get('fromurl', kw['homeurl'])
        if 'tourl' in desc:
            tourl = desc.get('tourl', '%(homeurl)s') % { 'homeurl': kw['homeurl']}
            project = req.POST.get('DMProject', '')
            if project != '': tourl = '%s?project=%s' % (tourl, project)
        return tourl
    
