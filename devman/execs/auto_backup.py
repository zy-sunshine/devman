#!/usr/bin/python

import glob, os.path, time

workdir = '/home/apache/devman'
date = time.strftime('%Y%m%d', time.localtime(time.time()))
projs = ['ebook', 'devman']
for proj in projs:
    svndir = os.path.join(workdir, 'svn', proj)
    svnbkfile = os.path.join(workdir, 'backup',
                             'svn-%s-%s.dump.bz2' % (proj, date))
    cmdline = 'svnadmin dump %s 2> /dev/null | bzip2 -9 > %s' % (svndir, svnbkfile)
    print(cmdline)
    os.system(cmdline)
    tracdir = os.path.join(workdir, 'trac', proj)
    tardir = os.path.join(workdir, 'trac')
    tracbkfile = os.path.join(workdir, 'backup',
                              'trac-%s-%s.tar.bz2' % (proj, date))
    dirlist = []
    for dirpath in glob.glob(os.path.join(tracdir, '*')):
        if os.path.relpath(dirpath, tracdir) == 'log': continue
        dirlist.append(os.path.relpath(dirpath, tardir))
    cmdline = 'tar c -C %s %s | bzip2 -9 > %s' % \
        (tardir, ' '.join(dirlist), tracbkfile)
    print(cmdline)
    os.system(cmdline)
