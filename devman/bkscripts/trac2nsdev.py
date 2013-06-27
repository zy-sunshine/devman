import os
import time
from sqlite3 import connect as sqlconn
from datetime import datetime

inConn = sqlconn('trac.db')
inCursor = inConn.cursor()

outConn = sqlconn('devman.sqlite3')
outCursor = outConn.cursor()

inTable1 = 'ticket'
inTable2 = 'version'
inTable3 = 'milestone'
inTable4 = 'component'

outTable1 = 'dmroot_dbentity'
outTable2 = 'nstask_dbtaskattrs'
outTable3 = 'dmroot_dbmember'
outTable4 = 'nstask_dbtaskparams'

project = 'bambook.mini'
trial = True

SEVERITIES = { "":       "minor"
             }

STATUS = { "":       "new",
           "assigned":  "new",
           "accepted":  "new"
         }

PRIORITIES = { "highest": "P1",
               "high":    "P2",
               "normal":  "P3",
               "low":     "P4",
               "lowest":  "P5",
               "major":   "P2",
               "minor":   "P4",
               "":        "P1",
               "None":    "P1"
               }

inrows = inCursor.execute('select * from %s' % inTable1).fetchall()
inColumn = [tuple[0] for tuple in inCursor.description]
outrows1 = outCursor.execute('select * from %s' % outTable1).fetchall()
outColumn1 = [tuple[0] for tuple in outCursor.description]
outrows2 = outCursor.execute('select * from %s' % outTable2).fetchall()
outColumn2 = [tuple[0] for tuple in outCursor.description]
outrows3 = outCursor.execute('select * from %s' % outTable3).fetchall()
outColumn3 = [tuple[0] for tuple in outCursor.description]
outrows4 = outCursor.execute('select * from %s' % outTable4).fetchall()
outColumn4 = [tuple[0] for tuple in outCursor.description]

print inColumn
print outColumn1
print outColumn2

# assign trac members to devman
if trial:
    members = ['admin']
    memrows = inCursor.execute('select * from %s' % inTable1).fetchall()
    outCursor.execute('delete from %s' % outTable3)
    for memrow in memrows:
        owners = memrow[7].split(',')
        reporters = memrow[8].split(',')
        for owner in owners:
            if owner in members: continue
            members.append(owner)
        for reporter in reporters:   
            if reporter not in members: continue
            members.append(reporter)
    memberid = 0      
    for member in members:
        memberid = memberid + 1
        rows = outCursor.execute('select * from %s where member="%s"' % (outTable3, member)).fetchall()
        if len(rows)>0: continue
        outCursor.execute('insert into dmroot_dbmember values (?, ?, ?, ?, ?, ?, ?, ?, ?)', (memberid, member,\
                                        1, member, memberid, '', '', 1, datetime.now()) )
 
# assign trac component, version, milestone to devman
execrows4 = []
params_id = 1
versions_row = 0
milestones_row = 0
components_row = 0
versions = inCursor.execute('select * from %s' % inTable2).fetchall()
milestones = inCursor.execute('select * from %s' % inTable3).fetchall()
components = inCursor.execute('select * from %s' % inTable4).fetchall()
outCursor.execute('delete from %s' % outTable4)
params = outCursor.execute('select * from %s order by id' % outTable4).fetchall()
if len(params) > 0: params_id = params[-1][0]
for version in versions:
    execrows4.append([params_id, project, '', 'version', versions_row, version[0]])
    params_id = params_id + 1
    versions_row = versions_row + 1
for milestone in milestones:
    execrows4.append([params_id, project, '', 'milestone', milestones_row, milestone[0]])
    params_id = params_id + 1
    milestones_row = milestones_row + 1
for component in components:
    execrows4.append([params_id, project, '', 'component', components_row, component[0]])
    params_id = params_id + 1
    components_row = components_row + 1
sql = 'insert into %s values (%s)' % (outTable4, ', '.join(['?'] * len(outColumn4)))
outCursor.executemany(sql, execrows4)

# entity columns
entity_rootid = 4
klass_bug_root = 'TaskRoot(bug)'
klass_bug = 'NSTask'

outCursor.execute('delete from %s where klass="%s" ' % (outTable1, klass_bug))
outCursor.execute('delete from %s' % outTable2)

entity_roots = outCursor.execute('select * from %s order by id' % outTable1).fetchall()
entity_curid = entity_roots[-1][0]

entity_bug = outCursor.execute('select * from %s where klass="%s"' % (outTable1, klass_bug_root)).fetchall()
if len(entity_bug) == 0:
    bug_rootid = entity_curid + 1
    entity_curid = bug_rootid
    outCursor.execute('insert into dmroot_dbentity values (?, ?, ?, ?, ?, ?)', (bug_rootid, entity_rootid,\
                                    klass_bug_root, 1, datetime.now(), datetime.now()) )
else:
    bug_rootid = entity_bug[0][0]
   
execrows1 = []
execrows2 = []

def member2id(member):
    dbobjs = outCursor.execute('select * from %s where member="%s"' % (outTable3, member)).fetchall()
    if len(dbobjs) == 0:  
        return 1
 #       raise ('Member %s is not present.') % repr(member)
    return dbobjs[0][0]
    
for inrow in inrows:
    nowdatetime = datetime.now()
    nowdate = nowdatetime.date()

    entity_curid = entity_curid + 1
    # init all entity columns
    execrow1 = []
    for i in range(0, len(outColumn1)):   
        execrow1.append('')
    # assign id to id
    execrow1[0] = entity_curid
    # assign bugrootid to parent
    execrow1[1] = bug_rootid
    # assign klass
    execrow1[2] = klass_bug
    # assign owner to owner
    execrow1[3] = member2id(inrow[7])
    # assign createtime
    execrow1[4] = nowdatetime
    # assign lastedittime
    execrow1[5] = nowdatetime
    execrows1.append(execrow1)
    
    # init all task attrs columns
    execrow2 = []
    for i in range(0, len(outColumn2)):   
        execrow2.append('')
    # assign id to id
    execrow2[0] = inrow[0]
    # assign task_id to 4
    execrow2[1] = entity_curid
    # assign project 
    execrow2[2] = project
    # assign type to bugdefect
    execrow2[56] = inrow[1]
    # assign time to begintime, endtime, maketime, reveiwtime, changetime
    execrow2[10] = nowdate
    execrow2[11] = nowdate
    execrow2[12] = nowdate
    execrow2[13] = nowdate
    execrow2[16] = nowdatetime
    # assign component to component
    execrow2[19] = inrow[4]
    # assign serverity to serverity
    if SEVERITIES.has_key(inrow[5]):
        execrow2[5] = SEVERITIES[inrow[5]]
    elif inrow[5] is None:
        execrow2[5] = 'minor'
    else:
        execrow2[5] = inrow[5]
    # assign priority to priority
    if PRIORITIES.has_key(inrow[6]):
        execrow2[4] = PRIORITIES[inrow[6]]
    else:
        execrow2[4] = inrow[6]
    # assign owner to owner
    execrow2[8] = member2id(inrow[7])
    # assign reporter to reporter
    execrow2[7] = inrow[8]
    # assign cc to cc
    execrow2[9] = member2id(inrow[9])
    # assign version to version
    execrow2[59] = inrow[10]
    # assign milestone to milestone
    execrow2[20] = inrow[11]
    # assign status to status
    if STATUS.has_key(inrow[12]):
        execrow2[57] = STATUS[inrow[12]]
    else:
        execrow2[57] = inrow[12]
    # assign summary to title
    execrow2[3] = inrow[14]
    # assign desc to desc
    execrow2[17] = inrow[15] 
    execrows2.append(execrow2)
 
sql = 'insert into %s values (%s)' % (outTable1, ', '.join(['?'] * len(outColumn1)))
outCursor.executemany(sql, execrows1)

sql = 'insert into %s values (%s)' % (outTable2, ', '.join(['?'] * len(outColumn2)))
outCursor.executemany(sql, execrows2)
outConn.commit()


