#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   Victor Lin
#   E-mail  :   linxianwusx@gmail.com
#   Date    :   15/01/31 18:26:29
#
import sae
import tornado.web
import sys
import time
import MySQLdb
import hashlib

def selectDbFromQrId(uuid):
    conn=MySQLdb.connect(host=sae.const.MYSQL_HOST,user=sae.const.MYSQL_USER,passwd=sae.const.MYSQL_PASS,db=sae.const.MYSQL_DB,port=int(sae.const.MYSQL_PORT),charset='utf8')
    cursor = conn.cursor()
    cursor.execute("select * from qrcode where QrId='%s'" % uuid)
    result = cursor.fetchone()
    if result:
        return result
    else:
        return -1

def insertDb(code, data, date):
    conn=MySQLdb.connect(host=sae.const.MYSQL_HOST,user=sae.const.MYSQL_USER,passwd=sae.const.MYSQL_PASS,db=sae.const.MYSQL_DB,port=int(sae.const.MYSQL_PORT),charset='utf8')
    cursor = conn.cursor()
    cursor.execute("update qrcode set Data = %s where QrId = %s",(data, code))
    cursor.execute("update qrcode set CreateTime = %s where QrId = %s",(date, code))
    conn.commit()
    cursor.close()
    conn.close()
    return True
    
def GetSecureId(qrcode):
    seed = 20121533
    nowtime = int(time.strftime('%m%d%H%M',time.localtime(time.time())))
    ostr = str(seed ^ nowtime)
    md5 = hashlib.md5((ostr+qrcode).encode('utf-8')).hexdigest()
    return md5
        
class GetQrcodeContent(tornado.web.RequestHandler):
    def get(self,uuid):
        reload(sys)
        sys.setdefaultencoding('utf-8')
        getuuid = selectDbFromQrId(uuid)
        if getuuid == -1:
            self.write('{"status" : "error"}')
        else:
            self.code, self.data,self.date = getuuid[1],getuuid[2],getuuid[3]
            if not self.data:
                self.write('{"status" : "blank"}')
            else:
                self.write('{"status" : "used" , ' +
                            '"code" : "' + self.code + '" , ' +
                            '"data" : "' + self.data + '" , ' +
                            '"date" : "' + self.date + '"}')
    def post(self,uuid):
        self.secureid = self.get_argument('secureid')
        self.code = uuid
        self.data = self.get_argument('data')
        self.date = self.get_argument('date')
        if self.secureid == GetSecureId(self.code):
            try:
                status = insertDb(self.code, self.data, self.date)
                print self.code,' ', self.data," ", self.date
                self.write('{"status" : "true"}')
            except:
                self.write('{"status" : "false"}')
        else:
            self.write('{"status" : "false"}')

