import imaplib
import smtplib
import email
import falcon
import json
from GlobalEnvironment.db import DB
from HTMLParser import HTMLParser
from GlobalEnvironment.GlobalFunctions import decryption, jwtDecode, sendmail

conn = DB()

class GlobalEmail(object):
    def emailValidation(self,username,password):
        try:
            SMTP_SERVER = "imap.gmail.com"
            mail = imaplib.IMAP4_SSL(SMTP_SERVER)
            login = mail.login(username, password)
            if login[0] == 'OK':
                return 1
            else:
                return False
        except:
            pass


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

class getEmail(object):
    def on_get(self, req, resp):
        try:
            EMAIL = "XXXXXXX"
            PASS  = "XXXXXXX"
            SMTP_SERVER = "imap.gmail.com"
            mail = imaplib.IMAP4_SSL(SMTP_SERVER)
            mail.login(EMAIL,PASS)

            mail.list()
            mail.select('inbox')

            type, data = mail.search(None, 'ALL')
            mail_ids = data[0]

            id_list = mail_ids.split()
            latest_email_id = int(id_list[-1])

            type, data = mail.fetch(latest_email_id, '(RFC822)')
            raw_email = data[0][1]
            msg = email.message_from_string(raw_email)
            decode = email.header.decode_header(msg['Subject'])[0]
            subject = unicode(decode[0])[:5]
            if msg.is_multipart():
                for payload in msg.get_payload():
                    body = payload.get_payload()
            else:
                body = msg.get_payload()

            if subject == '[REQ]' or subject == '[Req]' or subject == '[req]':
                if msg['cc'] is None:
                    cc = 0
                else:
                    em_cc = email.utils.getaddresses([msg['cc']])
                    cc = []
                    for mail in em_cc:
                        cc.append(mail[1])

                cekq = "select em_subject from email_task order by timestamp DESC limit 1"
                dataq = conn.select(cekq,None)
                dict = dataq[0]

                if dict.get('em_subject') != msg['subject']:
                    query = "insert into email_task (em_subject,em_from,em_cc,received,em_body) VALUES (%s,%s,%s,%s,%s)"
                    conn.query("insert", query, (msg['subject'],
                                                 email.utils.parseaddr(msg['From'])[1],
                                                 str(cc),
                                                 msg['date'],
                                                 body.replace('\r', '').replace('\n', '')))

                    callback = {"_dataemail": {
                        "subject": msg['subject'],
                        "from": email.utils.parseaddr(msg['From'])[1],
                        "cc": cc,
                        "received": msg['date'],
                        "body": body.replace('\r', '').replace('\n', '')
                    }
                    }

                    resp.set_header('Author-By', '@newbiemember')
                    resp.status = falcon.HTTP_200
                    resp.body = json.dumps(callback, sort_keys=True, indent=2, separators=(',', ': '))
                else:
                    callback = {"_dataemail": "Can't find new request to Infra", "status": False}
                    resp.set_header('Author-By', '@newbiemember')
                    resp.status = falcon.HTTP_200
                    resp.body = json.dumps(callback, sort_keys=True, indent=2, separators=(',', ': '))
            else:
                callback = {"_dataemail": "Can't find new request to infra", "status": False}
                resp.set_header('Author-By', '@newbiemember')
                resp.status = falcon.HTTP_200
                resp.body = json.dumps(callback, sort_keys=True, indent=2, separators=(',', ': '))

        except Exception, e:
            return str(e)

class sendEmailResponse(object):
    def on_post(self, req, resp):
        id_email = req.get_param('id_email')
        body_email= req.get_param('body_email')
        getQ = "select * from email_task where id_email=%s"
        dataQ= conn.query("select",getQ,id_email)
        dict = dataQ[0]

        if dict.get('em_cc') == 0:
            cc = None
        else:
            cc = dict.get('em_cc')

        toaddr = dict.get('em_from')
        token = req.get_header('Authorization')
        username,password = jwtDecode(token)
        subject = "Re: "+ dict.get('em_subject')

        #get secret from database for decript password:
        getq   = "select secret from members where username=%s"
        getq   = conn.query("select", getq,username)
        dict   = getq[0]

        secret = dict.get('secret')
        depassword = decryption(password,secret)
        if sendmail(username,toaddr,cc,subject,body_email,depassword) == 200:
            callback = {"sendmail": True }
            resp.set_header('Author-By', '@newbiemember')
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(callback, sort_keys=True, indent=2, separators=(',', ': '))
        else:
            callback = {"sendmail": False}
            resp.set_header('Author-By', '@newbiemember')
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(callback, sort_keys=True, indent=2, separators=(',', ': '))

