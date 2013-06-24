#!/usr/bin/python
import sys
from sqlite3 import connect as sqlconn

defargv = (None, 'devman.bk.sqlite3', 'devman.sqlite3')
argv = []
for pos in range(len(defargv)):
    if pos >= len(sys.argv): argv.append(defargv[pos])
    elif sys.argv[pos] == '.': argv.append(defargv[pos])
    else: argv.append(sys.argv[pos])
inconn = sqlconn(argv[1])
incursor = inconn.cursor()
outconn = sqlconn(argv[2])
outcursor = outconn.cursor()

class TableMap(object):
    def __init__(self):
        self.tbmap = {}

    def addtb(self, tbname, adds, subs):
        adds.sort()
        subs.sort()
        self.tbmap[tbname] = (adds, subs)

    def argvin(self, argvs):
        tbname = None
        adds = []
        subs = []
        for argv in argvs:
            if argv[0] == '+': adds.append(int(argv[1:]))
            elif argv[0] == '-': subs.append(int(argv[1:]))
            else:
                if tbname is not None: self.addtb(tbname, adds, subs)
                tbname = argv
                adds = []
                subs = []
        if tbname is not None: self.addtb(tbname, adds, subs)

    def updaterow(self, tbname, row):
        if tbname not in self.tbmap: return row
        row = list(row)
        delta = 0
        adds = self.tbmap[tbname][0]
        idxadd = 0
        subs = self.tbmap[tbname][1]
        idxsub = 0
        while idxadd < len(adds) or idxsub < len(subs):
            if idxadd == len(adds): oper = 'sub'
            elif idxsub == len(subs): oper = 'add'
            elif adds[idxadd] <= subs[idxsub]: oper = 'add'
            else: oper = 'sub'
            if oper == 'add':
                row.insert(delta + adds[idxadd], '')
                delta = delta + 1
                idxadd = idxadd + 1
            elif oper == 'sub':
                del(row[delta + subs[idxsub]])
                delta = delta - 1
                idxsub = idxsub + 1
        return row

    def update(self, incursor, outcursor):
        for tbname in self.tbmap.keys():
            rows = []
            for row in incursor.execute('SELECT * FROM %s' % tbname):
                rows.append(self.updaterow(tbname, row))
            if len(rows) > 0:
                outcursor.execute('DELETE FROM %s' % tbname)
                sql = 'INSERT INTO %s VALUES (%s)' % (tbname, ', '.join(['?'] * len(rows[0])))
                outcursor.executemany(sql, rows)

tbmap = TableMap()
tbmap.argvin(sys.argv[len(defargv):])
tbmap.update(incursor, outcursor)
outconn.commit()
