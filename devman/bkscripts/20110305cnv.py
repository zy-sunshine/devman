#!/usr/bin/python

from sqlite3 import connect as sqlconn

def set_row(row, pos, fv, tv):
    row = list(row)
    if row[pos] != fv:
        raise RuntimeError,\
            'row[%u] should be %u, but it is %u' % (pos, fv, row[pos])
    row[pos] = tv
    return tuple(row)

def update_member(row, pos):
    if row[pos] >= 32: return row
    return set_row(row, pos, row[pos], row[pos] + 1)

conn_r = sqlconn('devman.orig.sqlite3')
conn_w = sqlconn('devman.sqlite3')

cursor_r = conn_r.cursor()
cursor_w = conn_w.cursor()

print('For dmroot_member')
rows = list(cursor_r.execute('SELECT * FROM dmroot_member'))
rows = map(lambda row: update_member(row, 0), rows)
cursor_w.executemany('INSERT INTO dmroot_member VALUES (?, ?, ?, ?, ?, ?, ?, ?)', rows)
conn_w.commit()
cursor_w.execute('UPDATE dmroot_member SET jobnum=1 WHERE member="autobuild"')

print('For dmroot_idscope')
#rows = cursor_r.execute('SELECT * FROM dmroot_idscope')
cursor_w.execute('DELETE FROM dmroot_idscope')
cursor_w.execute('INSERT INTO dmroot_idscope VALUES (?, ?, ?, ?)', (1, 1, 2, 1000))
conn_w.commit()

print('For dmroot_idvalue')
rows = cursor_r.execute('SELECT * FROM dmroot_idvalue')
cursor_w.executemany('INSERT INTO dmroot_idvalue VALUES (?, ?, ?)', rows)
conn_w.commit()

print('For dmroot_memberprefs')
# nothing now.

print('For dmroot_memberroles')
rows = list(cursor_r.execute('SELECT * FROM dmroot_memberroles'))
rows = map(lambda row: update_member(row, 1), rows)
cursor_w.executemany('INSERT INTO dmroot_memberroles VALUES (?, ?, ?)', rows)
conn_w.commit()

print('For dmroot_perm')
rows = cursor_r.execute('SELECT * FROM dmroot_perm')
cursor_w.executemany('INSERT INTO dmroot_perm VALUES (?, ?)', rows)
conn_w.commit()

print('For dmroot_role')
rows = cursor_r.execute('SELECT * FROM dmroot_role')
cursor_w.executemany('INSERT INTO dmroot_role VALUES (?, ?)', rows)
conn_w.commit()

print('For dmroot_roleperms')
rows = cursor_r.execute('SELECT * FROM dmroot_roleperms')
cursor_w.executemany('INSERT INTO dmroot_roleperms VALUES (?, ?, ?)', rows)
conn_w.commit()

print('For nstool_randombatch')
rows = cursor_r.execute('SELECT * FROM nstool_randombatch')
rows = map(lambda row: update_member(row, 1), rows)
cursor_w.executemany('INSERT INTO nstool_randombatch VALUES (?, ?, ?, ?, ?, ?)', rows)
conn_w.commit()

print('For dmproj_project')
rows = cursor_r.execute('SELECT * FROM dmproj_project')
cursor_w.executemany('INSERT INTO dmproj_project VALUES (?, ?, ?, ?, ?)', rows)
conn_w.commit()

print('For nsaabill_billmonthcache')
rows = cursor_r.execute('SELECT * FROM nsaabill_billmonthcache')
rows = map(lambda row: update_member(row, 2), rows)
cursor_w.executemany('INSERT INTO nsaabill_billmonthcache VALUES (?, ?, ?, ?, ?, ?)', rows)
conn_w.commit()

print('For dmroot_entitydatetime')
# nothing now.
print('For dmroot_entityintegervalue')
# nothing now.
print('For dmroot_entitymember')
# nothing now.
print('For dmroot_entitypositiveintegervalue')
# Used by log only and abandon them now.
print('For dmroot_entitystringvalue')
# Used by log only and abandon them now.

billroot = 3
billklass = 'NSBill'
curentityid = 4
print('For nsaabill_bill')
rows = cursor_r.execute('SELECT * FROM nsaabill_bill')
billmap = {}
outrows = []
for row in rows:
    owner_id = row[2]
    if owner_id < 32: owner_id = owner_id + 1
    outrow = (curentityid, billroot, billklass, owner_id, row[1], row[1])
    billmap[row[0]] = outrow
    outrows.append(outrow)
    curentityid = curentityid + 1
cursor_w.executemany('INSERT INTO dmroot_entity VALUES (?, ?, ?, ?, ?, ?)', outrows)
conn_w.commit()

print('For nsaabill_billmember')
rows = cursor_r.execute('SELECT * FROM nsaabill_billmember')
outrows = []
for row in rows:
    bill_id = row[1]
    bill_id = billmap[bill_id][0]
    member_id = row[2]
    if member_id < 32: member_id = member_id + 1
    outrow = (row[0], bill_id, member_id, row[3])
    outrows.append(outrow)
cursor_w.executemany('INSERT INTO nsaabill_billmember VALUES (?, ?, ?, ?)', outrows)
conn_w.commit()

print('For nsaabill_billcomment')
rows = cursor_r.execute('SELECT * FROM nsaabill_billcomment')
outrows = []
cmtmap = {}
for row in rows:
    bill_id = row[1]
    billinfo = billmap[bill_id]
    bill_id = billinfo[0]
    outrow = (curentityid, bill_id, 'NSEntityComment', billinfo[3], billinfo[4], billinfo[5])
    text_id = row[2]
    cmtmap[text_id] = outrow
    outrows.append(outrow)
    curentityid = curentityid + 1
cursor_w.executemany('INSERT INTO dmroot_entity VALUES (?, ?, ?, ?, ?, ?)', outrows)
conn_w.commit()

curapiid = 1
attr = 0
fmap = { 'txt': 0, 'rst': 1 }
rows = cursor_r.execute('SELECT * FROM nstext_text')
outrows = []
for row in rows:
    text_id = row[0]
    cmtentityid = cmtmap[text_id][0]
    format = fmap[row[1]]
    outrow = (curapiid, cmtentityid, attr, format)
    outrows.append(outrow)
    curapiid = curapiid + 1
cursor_w.executemany('INSERT INTO dmroot_attrpositiveinteger VALUES (?, ?, ?, ?)', outrows)
conn_w.commit()

curctid = 1
rows = cursor_r.execute('SELECT * FROM nstext_textoriginal')
outrows = []
for row in rows:
    text_id = row[0]
    cmtentityid = cmtmap[text_id][0]
    outrow = (curctid, cmtentityid, row[2], row[3])
    outrows.append(outrow)
    curctid = curctid + 1
cursor_w.executemany('INSERT INTO dmroot_commenttext VALUES (?, ?, ?, ?)', outrows)
conn_w.commit()
