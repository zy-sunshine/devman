#!/bin/sh

DESTDIR=$1
prefix=/usr
etcdir=/etc/ssoauth
bindir=$prefix/bin
sbindir=$prefix/sbin/
nssdir=/lib
MACHINE_TYPE=`uname -m`
if [ "$MACHINE_TYPE" = 'x86_64' ]; then
  echo install on 64-bit...
  # 64-bit stuff here
  pamdir=/lib/security
else
  echo install on 32-bit...
  # 32-bit stuff here
  if [ -d /lib/i386-linux-gnu/security ]; then
    pamdir=/lib/i386-linux-gnu/security
  else
    pamdir=/lib/security
  fi
fi

mkdir -p $DESTDIR$etcdir
mkdir -p $DESTDIR$bindir
mkdir -p $DESTDIR$sbindir
mkdir -p $DESTDIR$pamdir

install -m 4770 -o git -g git srcs/sso-git-shell.exe $DESTDIR$bindir
install srcs/libnss_ssoauth.so $DESTDIR$nssdir/libnss_ssoauth.so.2
install srcs/sso-showuser.exe $DESTDIR$bindir
install srcs/ssoauth.exe $DESTDIR$sbindir
install srcs/ssoauth-dev.exe $DESTDIR$sbindir
install srcs/pam_ssolocal.so $DESTDIR$pamdir
install srcs/pam_ssoremote.so $DESTDIR$pamdir
install scripts/ssoauth_cache_update.py $DESTDIR$sbindir
install scripts/ssoauth_set_password.py $DESTDIR$sbindir
[ ! -f $DESTDIR$etcdir/shortcuts.txt ] && install -m 660 -o git -g git confs/shortcuts.txt $DESTDIR$etcdir
[ ! -f $DESTDIR$etcdir/ssousers.txt ] && install -m 660 -o git -g git confs/ssousers.txt $DESTDIR$etcdir
[ ! -f $DESTDIR$etcdir/ssoaccess.txt ] && install -m 660 -o git -g git confs/ssoaccess.txt $DESTDIR$etcdir
install -m 644 confs/etc-setup.patch $DESTDIR$etcdir

