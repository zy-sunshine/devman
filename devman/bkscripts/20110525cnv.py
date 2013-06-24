#!/usr/bin/python
import os
from sqlite3 import connect as sqlconn

inConn = sqlconn('devman.bbtrac.sqlite3')
inCursor = inConn.cursor()
outConn = sqlconn('devman.bbtrac.bk.sqlite3')
outCursor = outConn.cursor()

for inTable, outTable in (('nsaabill_dbbillmember', 'nsaabill_dbbillmember'),
                          ('nsaabill_dbbillmonthcache', 'nsaabill_dbbillmonthcache'),
                          ('dmproj_dbproject', 'dmproj_dbproject'),
                          ('dmroot_dbattrdatetime', 'dmroot_dbattrdatetime'),
                          ('dmroot_dbattrinteger', 'dmroot_dbattrinteger'),
                          ('dmroot_dbattrmember', 'dmroot_dbattrmember'),
                          ('dmroot_dbattrpositiveinteger', 'dmroot_dbattrpositiveinteger'),
                          ('dmroot_dbattrstring', 'dmroot_dbattrstring'),
                          ('dmroot_dbcommentcachedtext', 'dmroot_dbcommentcachedtext'),
                          ('dmroot_dbcommenttext', 'dmroot_dbcommenttext'),
                          ('dmroot_dbentity', 'dmroot_dbentity'),
                          ('dmroot_dbidscope', 'dmroot_dbidscope'),
                          ('dmroot_dbidvalue', 'dmroot_dbidvalue'),
                          ('dmroot_dbmember', 'dmroot_dbmember'),
                          ('dmroot_dbmemberprefs', 'dmroot_dbmemberprefs'),
                          ('dmroot_dbmemberroles', 'dmroot_dbmemberroles'),
                          ('dmroot_dbperm', 'dmroot_dbperm'),
                          ('dmroot_dbrole', 'dmroot_dbrole'),
                          ('dmroot_dbroleperms', 'dmroot_dbroleperms'),
                          ('nstool_dbrandombatch', 'nstool_dbrandombatch'),
                          ('nstask_dbtaskattrbasicgroup', 'nstask_dbtaskattrbasicgroup'),
                          ('nstask_dbtaskattrdemandgroup', 'nstask_dbtaskattrdemandgroup'),
                          ('nstask_dbtaskattrsupervisegroup', 'nstask_dbtaskattrsupervisegroup'),
                          ('nstask_dbtaskattrstategroup', 'nstask_dbtaskattrstategroup')):

    rows = list(inCursor.execute('SELECT * FROM %s' % inTable))
    if rows == []: continue
    print('From %s to %s with %u records' % (inTable, outTable, len(rows)))
    outCursor.execute('DELETE FROM %s' % outTable)
    sql = 'INSERT INTO %s VALUES (%s)' % (outTable, ', '.join(['?'] * len(rows[0])))
    outCursor.executemany(sql, rows)
outConn.commit()
