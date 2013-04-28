#!/usr/bin/python
# Usage: ssoauth_cache_update.py CACHE_DIR
# Query the original auth provider to update cache.

import os, pwd, sys, time, urllib2

cachedir = sys.argv[1]
gitpwd = pwd.getpwnam('git')

# Update ssoauth.txt
urlfmt = 'http://192.168.1.190:8090/magicsso/certify?orgname=hackos&user=%s&pwd=%s&sub=100001&ip=192.168.1.191'
rfn = os.path.join(cachedir, 'ssousers.txt')
wfn = os.path.join(cachedir, 'ssousers.new.txt')
rfp = open(rfn, 'rt')
wfp = open(wfn, 'wt')
wlns = 0
rln = rfp.readline()
while rln:
    vals = rln.strip().split('|')
    if vals[0] != 's' or vals[3] == '': wfp.write(rln); wlns = wlns + 1
    else:
        url = urlfmt % (vals[2].strip(), vals[3].strip())
        intext = urllib2.urlopen(url).read().split('|')
        if int(intext[0]) == 1: wfp.write(rln); wlns = wlns + 1
        else: vals[3] = ' ' * 32; wfp.write('|'.join(vals) + '\n')
    rln = rfp.readline()
wfp.close()
rfp.close()
os.rename(wfn, rfn)
os.chown(rfn, gitpwd.pw_uid, gitpwd.pw_gid)
os.chmod(rfn, 0660)
print('[%s] updated, %u lines written.' % (rfn, wlns))

# Update shortcuts.txt
nowstr = time.strftime('%Y%m%d%H', time.localtime(time.time()))
rfn = os.path.join(cachedir, 'shortcuts.txt')
wfn = os.path.join(cachedir, 'shortcuts.new.txt')
rfp = open(rfn, 'rt')
wfp = open(wfn, 'wt')
wlns = 0
rln = rfp.readline()
while rln:
    vals = rln.strip().split('|')
    if vals[0] == nowstr and vals[2] != 'root' and vals[2][-3:] != '-sh':
        wlns = wlns + 1
        wfp.write(rln)
    rln = rfp.readline()
wfp.close()
rfp.close()
os.rename(wfn, rfn)
os.chown(rfn, gitpwd.pw_uid, gitpwd.pw_gid)
os.chmod(rfn, 0660)
print('[%s] updated, %u lines written.' % (rfn, wlns))
