#!/bin/bash

HOMEDIR=/home/apache/devman
PROJ=$1
SVNDIR=$HOMEDIR/svn/$PROJ
TRACDIR=$HOMEDIR/trac/$PROJ

if test "x$HOMEDIR" == "x"; then
    echo HOMEDIR is blank.
    exit 10
fi

PERMSET0="BROWSER_VIEW CHANGESET_VIEW FILE_VIEW LOG_VIEW MILESTONE_VIEW"
PERMSET0="$PERMSET0 REPORT_SQL_VIEW REPORT_VIEW ROADMAP_VIEW SEARCH_VIEW"
PERMSET0="$PERMSET0 TICKET_VIEW TIMELINE_VIEW WIKI_VIEW"

PERMSET1="$PERMSET0 TICKET_CREATE TICKET_MODIFY WIKI_CREATE WIKI_MODIFY"

if test "x$PROJ" == "x"; then
    echo PROJ is blank.
    exit 11
elif test -e $SVNDIR; then
    echo $SVNDIR is exists!
    exit 12
elif test -e $TRACDIR; then
    echo $TRACDIR is exists!
    exit 13
else
    echo svnadmin create $SVNDIR
    svnadmin create $SVNDIR

    echo trac-admin $TRACDIR initenv $PROJ sqlite:db/trac.db svn $SVNDIR
    trac-admin $TRACDIR initenv $PROJ sqlite:db/trac.db svn $SVNDIR
    echo trac-admin $TRACDIR permission remove anonymous $PERMSET0
    trac-admin $TRACDIR permission remove anonymous $PERMSET0
    echo trac-admin $TRACDIR permission remove authenticated $PERMSET1
    trac-admin $TRACDIR permission remove authenticated $PERMSET1

    echo 'find $SVNDIR $TRACDIR -type f | xargs chmod 600'
    find $SVNDIR $TRACDIR -type f | xargs chmod 600

    echo 'find $SVNDIR $TRACDIR -type d | xargs chmod 700'
    find $SVNDIR $TRACDIR -type d | xargs chmod 700

    echo chown -R apache.apache $SVNDIR $TRACDIR
    chown -R apache.apache $SVNDIR $TRACDIR
    exit 0
fi
exit -1
