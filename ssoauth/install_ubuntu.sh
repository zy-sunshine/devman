#!/bin/sh

DESTDIR=$1
prefix=/usr
etcdir=/etc/ssoauth
bindir=$prefix/bin
sbindir=$prefix/sbin/
nssdir=/lib
pamdir=/lib/security
apache_confdir=/etc/apache2
apache_modules_confdir=$apache_confdir/mods-available
apache_modules_confdir_en=$apache_confdir/mods-enabled
apache_docroot=/var/www/localhost/htdocs

mkdir -p $DESTDIR$etcdir
mkdir -p $DESTDIR$bindir
mkdir -p $DESTDIR$sbindir
mkdir -p $DESTDIR$pamdir
mkdir -p $DESTDIR$apache_modules_confdir
mkdir -p $DESTDIR$apache_docroot/ssoauth-test
mkdir -p $DESTDIR$apache_docroot/ssoauth-dev-test

install -m 4770 -o git -g git srcs/sso-git-shell.exe $DESTDIR$bindir
install srcs/libnss_ssoauth.so $DESTDIR$nssdir/libnss_ssoauth.so.2
install srcs/sso-showuser.exe $DESTDIR$bindir
install srcs/ssoauth.exe $DESTDIR$sbindir
install srcs/ssoauth-dev.exe $DESTDIR$sbindir
install srcs/pam_ssolocal.so $DESTDIR$pamdir
install srcs/pam_ssoremote.so $DESTDIR$pamdir
install scripts/ssoauth_cache_update.py $DESTDIR$sbindir
install scripts/ssoauth_set_password.py $DESTDIR$sbindir
install -m 660 -o git -g git confs/shortcuts.txt $DESTDIR$etcdir
install -m 660 -o git -g git confs/ssousers.txt $DESTDIR$etcdir
install -m 660 -o git -g git confs/ssoaccess.txt $DESTDIR$etcdir
install -m 644 confs/90_ssoauth.conf $DESTDIR$apache_modules_confdir
install -m 644 confs/91_ssoauth_test.conf $DESTDIR$apache_modules_confdir
ln -sv ../mods-available/90_ssoauth.conf $DESTDIR$apache_modules_confdir_en/90_ssoauth.conf
ln -sv ../mods-available/91_ssoauth_test.conf $DESTDIR$apache_modules_confdir_en/91_ssoauth_test.conf
install -m 644 confs/etc-setup.patch $DESTDIR$etcdir
install -m 644 srcs/ssoauth.html $DESTDIR$apache_docroot/ssoauth-test/index.html
install -m 644 srcs/ssoauth-test.html $DESTDIR$apache_docroot/ssoauth-dev-test/index.html
