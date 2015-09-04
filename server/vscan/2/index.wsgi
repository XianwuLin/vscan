# -*- coding:utf-8 -*-
import tornado.web
from tornado.httpclient import AsyncHTTPClient
import json
import urllib
from Crypto.Cipher import AES
import base64
import sys
reload(sys)
sys.setdefaultencoding('utf8')

PADDING = '\0'

def txt2html(txt):
    def escape(txt):
        '''将txt文本中的空格、&、<、>、（"）、（'）转化成对应的的字符实体，以方便在html上显示'''
        txt = txt.replace('&','&#38;')
        txt = txt.replace(' ','&#160;')
        txt = txt.replace('<','&#60;')
        txt = txt.replace('>','&#62;')
        txt = txt.replace('"','&#34;')
        txt = txt.replace('\'','&#39;')
        return txt

    txt = escape(txt)
    lines = txt.split('\n')
    for i, line in enumerate(lines):
        lines[i] = unicode('<p>', "utf-8") + line + unicode('</p>', "utf-8")
    txt = ''.join(lines)
    return txt

def desEncrypt(crypted):
    key = 'xianwuVictor2134'
    iv = '1234567812345678'
    decrypten = base64.b64decode(crypted)
    generator = AES.new(key, AES.MODE_CBC, iv)
    recovery = generator.decrypt(decrypten)
    return recovery.rstrip(PADDING).decode('UTF-8')

def get_content(data):
    s = (json.loads(data))["content"]

def get_att(qrcode):
    f=urllib.urlopen("http://linxianwu.sinaapp.com/qrcode/"+qrcode)
    return_str = f.read()
    s=json.loads(return_str, strict=False)
    return s

class MainHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.write("This is linxianwu's website")
        self.finish()

    def _callback(self, response):
        self.write(response.body)
        self.finish()
        
class QrCode(tornado.web.RequestHandler):
    def get(self,uuid):
        data = get_att(uuid)
        status = data["status"]
        audiotext = ""
        if status == "error":
            text = "错误的二维码"
        elif status == "blank":
            text = "这个二维码没有用过"
        elif status == "used":
            content = json.loads(desEncrypt(data["data"]))["content"]
            audio = json.loads(desEncrypt(data["data"]))["audio"]
            text = txt2html(content)
            if (audio != "null"):
                audiotext = '<p>有录音哦，打开App他说了什么~</p>'
        self.render("index.html",Qrcode = uuid, Data = text, Image = "http://qr.liantu.com/api.php?m=5&w=150&el=q&logo=http://i2.tietuku.com/ba066af48fa5677a.png&text=http://vscan.sinaapp.com/qrcode/"+uuid, Audio = audiotext)


settings = {
    "debug": True,
}

# application should be an instance of `tornado.web.Application`,
# and don't wrap it with `sae.create_wsgi_app`
application = tornado.web.Application([
    (r"/", MainHandler),
    (r'/qrcode/(\S+)', QrCode),
], **settings)
