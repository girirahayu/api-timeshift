import imaplib
import email
import falcon
import json
from GlobalEnvironment.db import DB
from HTMLParser import HTMLParser
import datetime
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
            date = (datetime.date.today() - datetime.timedelta(1)).strftime("%d-%b-%Y")
            result, data = mail.uid('search', None, '(SENTSINCE {date} HEADER Subject "[REQ]")'.format(date=date))  # search and return uids instead
            latest_email_uid = data[0].split()[-1]
            result, data = mail.uid('fetch', latest_email_uid, '(RFC822)')
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

                cekq = "select em_subject from email_receive order by timestamp DESC limit 1"
                dataq = conn.select(cekq,None)
                dict = dataq[0]

                if dict.get('em_subject') != msg['subject']:
                    query = "insert into email_receive (em_subject,em_from,em_cc,received,em_body) VALUES (%s,%s,%s,%s,%s)"
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
        status = int(req.get_param('status'))
        getQ = "select * from email_receive where id_email=%s"
        dataQ= conn.query("select",getQ,id_email)
        dict = dataQ[0]

        if dict.get('em_cc') == str(0):
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
            if status == 0:
                qin = "insert into email_tasklist (username_member,id_email,response) VALUES (%s,%s,now())"
                conn.query("insert", qin, (username,id_email))

                callback = {"sendmail": True, "response-by": username }
                resp.set_header('Author-By', '@newbiemember')
                resp.status = falcon.HTTP_200
                resp.body = json.dumps(callback, sort_keys=True, indent=2, separators=(',', ': '))
            else:
                qup = "update email_tasklist set status=%s, selesai=now() where id_email=%s and status=0"
                conn.query("update", qup, (1, id_email))
                callback = {"sendmail": True, "finish-by": username}
                resp.set_header('Author-By', '@newbiemember')
                resp.status = falcon.HTTP_200
                resp.body = json.dumps(callback, sort_keys=True, indent=2, separators=(',', ': '))
        else:
            callback = {"sendmail": False}
            resp.set_header('Author-By', '@newbiemember')
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(callback, sort_keys=True, indent=2, separators=(',', ': '))

