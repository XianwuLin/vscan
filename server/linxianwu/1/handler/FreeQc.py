#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   Victor Lin
#   E-mail  :   linxianwusx@gmail.com
#   Date    :   15/02/04 19:59:23
#
import sae
import tornado.web
import shortuuid
import datetime
import time
import MySQLdb
import base64

applyTime = 30

def checkClientId(secureclientId):
    try:
        cryptenStr = base64.b64decode(secureclientId)
        if cryptenStr[0] == 'a' and cryptenStr[7] == '3' and cryptenStr[-3] == '3' and cryptenStr[-1] == '0':
            return True
        else:
            return False
    except:
        return False

def getUuid():
    return shortuuid.ShortUUID().random(length=22)

def selectFreeqcFromClientId(clientId):
    conn = MySQLdb.connect(host=sae.const.MYSQL_HOST,user=sae.const.MYSQL_USER,passwd=sae.const.MYSQL_PASS,db=sae.const.MYSQL_DB,port=int(sae.const.MYSQL_PORT),charset='utf8')
    cursor = conn.cursor()
    cursor.execute("select * from freeqc where ClientId='%s'" % clientId)
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result:
        return result
    else:
        return -1

def selectQrcodeFromqrcode(qrcode):
    conn = MySQLdb.connect(host=sae.const.MYSQL_HOST,user=sae.const.MYSQL_USER,passwd=sae.const.MYSQL_PASS,db=sae.const.MYSQL_DB,port=int(sae.const.MYSQL_PORT),charset='utf8')
    cursor = conn.cursor()
    cursor.execute("select * from qrcode where QrId='%s'" % qrcode)
    result =  cursor.fetchone()
    cursor.close()
    conn.close()
    return result

def insertIntoFreeqc(clientId):
    conn=MySQLdb.connect(host=sae.const.MYSQL_HOST,user=sae.const.MYSQL_USER,passwd=sae.const.MYSQL_PASS,db=sae.const.MYSQL_DB,port=int(sae.const.MYSQL_PORT),charset='utf8')
    cursor = conn.cursor()
    uuid = getUuid()
    dtn = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    if selectFreeqcFromClientId(clientId) == -1:
        # 从未注册过 要insert
        cursor.execute("insert into freeqc (ClientId,Qrcode,ApplyTime) values (%s,%s,%s)",(clientId, uuid, dtn))
    else:
        # 注册过，要update
        cursor.execute("update freeqc set Qrcode = %s where ClientId = %s",(uuid, clientId))
        cursor.execute("update freeqc set Qrcode = %s where ApplyTime = %s",(uuid, dtn))
    cursor.execute("insert into qrcode (QrId) values (%s)",(uuid,))
    conn.commit()
    cursor.close()
    conn.close()
    return uuid

class FreeQc(tornado.web.RequestHandler):
    def post(self):
        global applyTime
        clientId = self.get_argument('Id')
        print "ID  ---->  ", clientId
        if checkClientId(clientId): 
            self.clientId = clientId
            ci = selectFreeqcFromClientId(self.clientId)
            if ci == -1:
                # 从未申请过二维码
                self.qrcode = insertIntoFreeqc(self.clientId)
                print self.qrcode
                self.write('{"status" : "blank" , ' +
                                '"code" : "' + self.qrcode + '"}')
            else:  #申请过二维码
                self.qrcode, self.applyTime = ci[2], ci[3]
                ct = selectQrcodeFromqrcode(self.qrcode)
                self.data = ct[2]
                print "data '" + self.data + "'"
                if (self.data): # 已使用
                    now = datetime.datetime.now()
                    used = datetime.datetime.strptime(self.applyTime,"%Y-%m-%d %H:%M:%S")
                    usedMinutes = (now - used).seconds
                    if usedMinutes >= (applyTime * 60):
                        # todo 二维码过期
                        self.qrcode = insertIntoFreeqc(self.clientId)
                        print self.qrcode
                        self.write('{"status" : "blank" , ' +
                                    '"code" : "' + self.qrcode + '"}')
                    else:
                        self.write('{"status" : "used"}')
                else: # 二维码未使用
                    self.qrcode = insertIntoFreeqc(self.clientId)
                    print self.qrcode
                    self.write('{"status" : "blank" , ' +
                            '"code" : "' + self.qrcode + '"}')
        else:
            self.write('{"status" : "error"}')
