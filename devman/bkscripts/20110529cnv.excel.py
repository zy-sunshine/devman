#!/usr/bin/python
import xlrd
import os
from datetime import datetime
from sqlite3 import connect as sqlconn

dict = {'demand_excel': 'Bambook_20110520.xls',
        'supervise_excel': '',
        'state_excel': '',
        'dbname':'devman.sqlite3',
        'sheets': [1 , 2,  3 , 4]
    }

demand_excel = dict['demand_excel']
supervise_excel = dict['supervise_excel']
state_excel = dict['state_excel']
sheets = dict['sheets']
dbname = dict['dbname']

dbConn = sqlconn(dbname)
dbCursor = dbConn.cursor()

demand_klass = 'TaskRoot(demand)'
supervise_klass = 'TaskRoot(supervise)'
state_klass = 'TaskRoot(state)'

entity_roots = dbCursor.execute('SELECT * FROM dmroot_dbentity ORDER BY id').fetchall()
entity_rootid = 4
entity_curid = entity_roots[-1][0]

entity_demands = dbCursor.execute('SELECT * FROM dmroot_dbentity WHERE klass="%s"' % demand_klass).fetchall()
if len(entity_demands) == 0:
    entity_curid = entity_curid + 1
    dbCursor.execute('INSERT INTO dmroot_dbentity VALUES (?, ?, ?, ?, ?, ?)', (entity_curid, entity_rootid,\
                                    demand_klass, 1, datetime.now(), datetime.now()))
    entity_demand = [entity_curid, entity_rootid, demand_klass, 1, datetime.now(), datetime.now()]
else:
    entity_demand = entity_demands[0]
     
entity_supervises = dbCursor.execute('SELECT * FROM dmroot_dbentity WHERE klass="%s"' % supervise_klass).fetchall()
if len(entity_supervises) == 0:
    entity_curid = entity_curid + 1
    entity_supervise = dbCursor.execute('INSERT INTO dmroot_dbentity VALUES (?, ?, ?, ?, ?, ?)', (entity_curid, entity_rootid,\
                                    supervise_klass, 1, datetime.now(), datetime.now()))
    entity_supervise = [entity_curid, entity_rootid, supervise_klass, 1, datetime.now(), datetime.now()]
else:
    entity_supervise = entity_supervises[0]
    
entity_states = dbCursor.execute('SELECT * FROM dmroot_dbentity WHERE klass="%s"' % state_klass).fetchall()
if len(entity_states) == 0:
    entity_curid = entity_curid + 1
    entity_state = dbCursor.execute('INSERT INTO dmroot_dbentity VALUES (?, ?, ?, ?, ?, ?)', (entity_curid, entity_rootid,\
                                    state_klass, 1, datetime.now(), datetime.now()))
    entity_state = [entity_curid, entity_rootid, state_klass, 1, datetime.now(), datetime.now()]
else:
    entity_state = entity_states[0]

basic_rows = dbCursor.execute('SELECT * FROM nstask_dbtaskattrbasicgroup ORDER BY id').fetchall()
if len(basic_rows) == 0:
    basic_curid = 1
else:
    basic_curid = basic_rows[-1][0]

demand_rows = dbCursor.execute('SELECT * FROM nstask_dbtaskattrdemandgroup ORDER BY id').fetchall()
if len(demand_rows) == 0:
    demand_curid = 1
else:
    demand_curid = demand_rows[-1][0]
    
supervise_rows = dbCursor.execute('SELECT * FROM nstask_dbtaskattrsupervisegroup ORDER BY id').fetchall()
if len(supervise_rows) == 0:
    supervise_curid = 1
else:
    supervise_curid = supervise_rows[-1][0]
    
state_rows = dbCursor.execute('SELECT * FROM nstask_dbtaskattrstategroup ORDER BY id').fetchall()
if len(state_rows) == 0:
    state_curid = 1
else:
    state_curid = state_rows[-1][0]
 
# add demand table to db

try:
    bk = xlrd.open_workbook(demand_excel)
    sh = bk.sheets()[1]
    nrows = sh.nrows
    ncols = sh.ncols
except:
    nrows = 0
    ncols = 0
    print '***********can not open demand table************'

print "demand table is nrows %d, ncols %d" % (nrows,ncols)
append_rows = []

for rownum in range(2, nrows):
    rowvalues = sh.row_values(rownum)
    if rowvalues[0] != '':
        entity_curid = entity_curid +1
        # add record into dbentity table
        dbCursor.execute('INSERT INTO dmroot_dbentity VALUES (?, ?, ?, ?, ?, ?)', (entity_curid, entity_demand[0],\
                                'NSTask', 1, datetime.now(), datetime.now()))
        # add record into bastc table
        basic_curid = basic_curid + 1
        rowvalues[7] = 'Audited'
        rowvalues[11] = '1'
        dbCursor.execute('INSERT INTO nstask_dbtaskattrbasicgroup VALUES (?, ?, ?, ?, ?, ?, ?)', (basic_curid, entity_curid,\
                                '', rowvalues[7], rowvalues[11], '', ''))
        # add record into demand table
        demand_curid = demand_curid + 1
        rowvalues[2] = 'BaseSystem'
        rowvalues[3] = 'Customer'
        dbCursor.execute('INSERT INTO nstask_dbtaskattrdemandgroup VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',\
                                (demand_curid, entity_curid, rowvalues[0], rowvalues[2], 'IDDesign3', rowvalues[3], rowvalues[4], \
                                 rowvalues[12], rowvalues[9], rowvalues[10], rowvalues[13], '', '',rowvalues[14]))
dbConn.commit()
print 'demand table transfer is ok!' 


# add supervise table to db
try:
    bk = xlrd.open_workbook(supervise_excel)
    sh = bk.sheets()[1]
    nrows = sh.nrows
    ncols = sh.ncols
except:
    nrows = 0
    ncols = 0
    print '***********can not open supervise table************'
    
print "sypervise table is nrows %d, ncols %d" % (nrows,ncols)
append_rows = []

for rownum in range(2, nrows):
    rowvalues = sh.row_values(rownum)
    if rowvalues[0] != '':
        entity_curid = entity_curid +1
        # add record into dbentity table
        dbCursor.execute('INSERT INTO dmroot_dbentity VALUES (?, ?, ?, ?, ?, ?)', (entity_curid, entity_supervise[0],\
                                'NSTask', 1, datetime.now(), datetime.now()))
        # add record into basic table
        basic_curid = basic_curid + 1
        rowvalues[9] = 'Closed'
        rowvalues[4] = 'admin'
        dbCursor.execute('INSERT INTO nstask_dbtaskattrbasicgroup VALUES (?, ?, ?, ?, ?, ?, ?)', (basic_curid, entity_curid,\
                                '', rowvalues[9], rowvalues[4], '', ''))
        # add record into supervise table
        supervise_curid = supervise_curid + 1
        dbCursor.execute('INSERT INTO nstask_dbtaskattrsupervisegroup VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',\
                                (supervise_curid, entity_curid, rowvalues[1], rowvalues[2], rowvalues[3], rowvalues[5], \
                                 rowvalues[6], rowvalues[7], rowvalues[8], rowvalues[10], rowvalues[11]))

dbConn.commit()
print 'supervise table transfer is ok!' 


# add state table to db
try:
    sh = bk.sheets()[1]
    bk = xlrd.open_workbook(state_excel)
    nrows = sh.nrows
    ncols = sh.ncols
except:
    nrows = 0
    ncols = 0
    print '***********can not open state table************'

print "state table is nrows %d, ncols %d" % (nrows,ncols)
append_rows = []

for rownum in range(2, nrows):
    rowvalues = sh.row_values(rownum)
    if rowvalues[0] != '':
        entity_curid = entity_curid +1
        # add record into dbentity table
        dbCursor.execute('INSERT INTO dmroot_dbentity VALUES (?, ?, ?, ?, ?, ?)', (entity_curid, entity_state[0],\
                                'NSTask', 1, datetime.now(), datetime.now()))
        # add record into basic table
        basic_curid = basic_curid + 1
        rowvalues[2] = 'Closed'
        dbCursor.execute('INSERT INTO nstask_dbtaskattrbasicgroup VALUES (?, ?, ?, ?, ?, ?, ?)', (basic_curid, entity_curid,\
                                '', rowvalues[2], '', '', ''))
        # add record into state table
        state_curid = state_curid + 1
        dbCursor.execute('INSERT INTO nstask_dbtaskattrstategroup VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',\
                                (state_curid, entity_curid, rowvalues[1], rowvalues[3], rowvalues[4], rowvalues[5], \
                                 rowvalues[6], rowvalues[7], rowvalues[8]))


dbConn.commit()
print 'state table transfer is ok!' 




