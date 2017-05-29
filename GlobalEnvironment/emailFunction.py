import imaplib
import email
import falcon
import json
from HTMLParser import HTMLParser

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
            EMAIL = "XXXXXXXXX"
            PASS  = "XXXXXXXXX"
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

            #body = msg.get_payload()[0].get_payload()
            if msg.is_multipart():
                for payload in msg.get_payload():
                    # if payload.is_multipart(): ...
                    body =  payload.get_payload()
            else:
                    body = msg.get_payload()

            data = {"_data" : {
                        "subject" : msg['subject'],
                        "from"    : email.utils.parseaddr(msg['From'])[1],
                        "cc"      : msg['cc'].replace('\r','').replace('\n','').replace('\t',''),
                        "body"    : body.replace('\r','').replace('\n',''),
                        "received" : msg['date']
                    }
            }

            resp.set_header('Author-By', '@newbiemember')
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(data, sort_keys=True, indent=2, separators=(',', ': '))


        except Exception, e:
            return str(e)
