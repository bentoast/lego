#!/usr/bin/env python3

import os
import json
import cgitb
import MySQLdb

cgitb.enable()

settingsFile = os.path.expanduser('/home/pi/Lego/settings.ini')
openFile = open(settingsFile)
settings = json.load(openFile)
openFile.close()

def getAll(statement, params):
    con = MySQLdb.connect(settings['host'], settings['user'], settings['password'], settings['db'])
    cur = con.cursor()
    
    cur.execute(statement, params)
    return cur.fetchall()
    
def getOne(statement, params):
    con = MySQLdb.connect(settings['host'], settings['user'], settings['password'], settings['db'])
    cur = con.cursor()
    
    cur.execute(statement, params)
    return cur.fetchone()
    
def insertrow(statement, params):
    con = MySQLdb.connect(settings['host'], settings['user'], settings['password'], settings['db'])
    cur = con.cursor()
    
    cur.execute(statement, params)
    con.commit()
    return True

def updaterow(statement, params):
    con = MySQLdb.connect(settings['host'], settings['user'], settings['password'], settings['db'])
    cur = con.cursor()
    
    cur.execute(statement, params)
    con.commit()
    return True
    
def deleterow(statement, params):
    con = MySQLdb.connect(settings['host'], settings['user'], settings['password'], settings['db'])
    cur = con.cursor()
    
    cur.execute(statement, params)
    con.commit()
    return True