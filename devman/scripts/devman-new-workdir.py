#!/usr/bin/python

import os, os.path, sys
import sqlite3
from django.core.management import execute_manager

if len(sys.argv) != 2:
    os.write(2, 'Usage: %s CFGTEXT' % sys.argv[0])
    sys.exit(1)

if os.getlogin() != 'apache':
    os.write(2, 'Run this script with usr "apache"')
    sys.exit(1)

inf = open(sys.argv[1], 'rt')
cfg = (inf.readline().strip(),
       inf.readline().strip(),
       inf.readline().strip())
inf.close()

def ensure_dir(dirpath):
    if not os.path.exists(dirpath): os.mkdir(dirpath, 0700)
    elif not os.path.isdir(dirpath):
        raise RuntimeError, '%s must be a dir.' % dirpath

print("Setup dir structures.")
cwd = os.getcwd()
os.symlink(os.path.join(os.path.dirname(__file__), 'devman-manage.py'),
           os.path.join(cwd, 'manage.py'))
os.symlink(os.path.join(os.path.dirname(__file__), 'devman.wsgi'),
           os.path.join(cwd, 'devman.wsgi'))
ensure_dir(os.path.join(cwd, 'svn'))
ensure_dir(os.path.join(cwd, 'trac'))

print("Sync DB")
os.environ['DEVMAN_WORKDIR'] = os.path.abspath(os.getcwd())
import devman.settings
execute_manager(devman.settings, argv = [sys.argv[0], 'syncdb'])
os.chmod('devman.sqlite3', 0600)

print("Setup the initial manager user")
conn = sqlite3.connect('devman.sqlite3')
c = conn.cursor()
c.execute("INSERT INTO dmroot_member VALUES (0, '%s', '%s', '%s', 1);" % cfg)
conn.commit()
c.close()
