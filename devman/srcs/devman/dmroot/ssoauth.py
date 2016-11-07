import os.path
from devman.settings import ssoauthdir

# RELATED VALUES: A */
def SsoUsersGet(ln):
    lnarr = ln.split('|')
    kw = {}
    for kn in ('usertype', 'uid', 'user', 'enchexpwd'):
        kw[kn] = lnarr.pop(0).strip()
    kw['uid'] = int(kw['uid'])
    return kw

def SsoUsersSet(usertype, uid, user, enchexpwd):
    return "%c|%-8u|%-32s|%-32s" % (usertype, uid, user, enchexpwd)

# RELATED VALUES: B */
def SsoAccessGet(ln):
    lnarr = ln.split('|')
    kw = {}
    for kn in ('sstype', 'user', 'ip', 'subsys'):
        kw[kn] = lnarr.pop(0).strip()
    return kw

def SsoAccessSet(sstype, user, ip, subsys):
    if ip is None: ip = ''
    return "%c|%-32s|%-16s|%-32s" % (sstype, user, ip, subsys)

def SsoUsersAddOrEdit(usertype, uid, user, enchexpwd):
    ssousers_fn = os.path.join(ssoauthdir, 'ssousers.txt')
    if not os.path.isfile(ssousers_fn): ssouserslns = []
    else: ssouserslns = open(ssousers_fn, 'rt').read().splitlines()
    userln = SsoUsersSet(usertype, uid, user, enchexpwd) + '\n'
    writeset = []
    for ln in ssouserslns:
        userkw = SsoUsersGet(ln)
        if userkw['user'] != user: writeset.append(ln + '\n')
        elif userln:
            writeset.append(userln)
            userln = None
    if userln: writeset.append(userln)
    content = ''.join(writeset)
    open(ssousers_fn, 'rt+').write(content)

def SsoUsersDel(user):
    ssousers_fn = os.path.join(ssoauthdir, 'ssousers.txt')
    if not os.path.isfile(ssousers_fn): ssouserslns = []
    else: ssouserslns = open(ssousers_fn, 'rt').read().splitlines()
    writeset = []
    for ln in ssouserslns:
        userkw = SsoUsersGet(ln)
        if userkw['user'] != user: writeset.append(ln + '\n')
    content = ''.join(writeset)
    open(ssousers_fn, 'rt+').write(content)

