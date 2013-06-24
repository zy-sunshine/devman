#!/usr/bin/python
import os
from sqlite3 import connect as sqlconn

inConn = sqlconn('devman.bbtrac.sqlite3')
inCursor = inConn.cursor()
outConn = sqlconn('devman.blank.sqlite3')
outCursor = outConn.cursor()

for inTable, outTable in (('nsaabill_billmember', 'nsaabill_dbbillmember'),
                          ('nsaabill_billmonthcache', 'nsaabill_dbbillmonthcache'),
                          ('dmproj_project', 'dmproj_dbproject'),
                          ('dmroot_attrdatetime', 'dmroot_dbattrdatetime'),
                          ('dmroot_attrinteger', 'dmroot_dbattrinteger'),
                          ('dmroot_attrmember', 'dmroot_dbattrmember'),
                          ('dmroot_attrpositiveinteger', 'dmroot_dbattrpositiveinteger'),
                          ('dmroot_attrstring', 'dmroot_dbattrstring'),
                          ('dmroot_commentcachedtext', 'dmroot_dbcommentcachedtext'),
                          ('dmroot_commenttext', 'dmroot_dbcommenttext'),
                          ('dmroot_entity', 'dmroot_dbentity'),
                          ('dmroot_idscope', 'dmroot_dbidscope'),
                          ('dmroot_idvalue', 'dmroot_dbidvalue'),
                          ('dmroot_member', 'dmroot_dbmember'),
                          ('dmroot_memberprefs', 'dmroot_dbmemberprefs'),
                          ('dmroot_memberroles', 'dmroot_dbmemberroles'),
                          ('dmroot_perm', 'dmroot_dbperm'),
                          ('dmroot_role', 'dmroot_dbrole'),
                          ('dmroot_roleperms', 'dmroot_dbroleperms'),
                          ('nstool_randombatch', 'nstool_dbrandombatch')):

    rows = list(inCursor.execute('SELECT * FROM %s' % inTable))
    if rows == []: continue
    print('From %s to %s with %u records' % (inTable, outTable, len(rows)))
    outCursor.execute('DELETE FROM %s' % outTable)
    sql = 'INSERT INTO %s VALUES (%s)' % (outTable, ', '.join(['?'] * len(rows[0])))
    outCursor.executemany(sql, rows)
outConn.commit()
