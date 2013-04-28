#!/usr/bin/python

import sys
import re
import StringIO
try:
    from hashlib import md5
except ImportError:
    import md5

#auth_txt = '/etc/ssoauth/ssoauth.txt'
auth_txt = './ssoauth.txt'

def usage(main):
    print '''
set a username/password pair to replace original ssoauth pair, available for one day.
Usage: %s username password
    ''' % main

def set_password(username, password):
    s = StringIO.StringIO()
    with open(auth_txt, 'r') as f:
        for line in f.readlines():
            if line.endswith('|%s\n' % username):
                continue
            s.write(line)
    s.write('%s|%s\n' % (md5(password).hexdigest().upper(), username))
    with open(auth_txt, 'w') as f:
        f.write(s.getvalue())
    s.close()

if __name__ == '__main__':
    if len(sys.argv) == 1 or sys.argv[1] in ('-h', '--help', 'help'):
        usage(sys.argv[0])
        sys.exit(0)
    if len(sys.argv) != 3:
        print >> stderr, 'please input username password.'
        sys.exit(1)
    set_password(sys.argv[1], sys.argv[2])
