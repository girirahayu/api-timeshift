import imaplib
import email
import falcon
import json
from GlobalEnvironment.db import DB
import datetime
from GlobalEnvironment.GlobalFunctions import decryption, jwtDecode, sendmail, sendTelegram, sendToRabbit
JWT_SECRET = 'infra@codigo'
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 20
conn = DB()


def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    raise TypeError("Unknown type")

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

                cekq = "select count(em_subject) as count from email_receive where em_subject=%s and received=%s order by timestamp DESC limit 1"
                dataq = conn.query("select",cekq,(msg['subject'],msg['date']))
                dict = dataq[0]

                if dict.get('count') == 0:
                    query = "insert into email_receive (em_subject,em_from,em_cc,received,em_body) VALUES (%s,%s,%s,%s,%s)"
                    conn.query("insert", query, (msg['subject'],
                                                 email.utils.parseaddr(msg['From'])[1],
                                                 str(cc),
                                                 msg['date'],
                                                 body))

                    callback = {"_dataemail": {
                        "subject": msg['subject'],
                        "from": email.utils.parseaddr(msg['From'])[1],
                        "cc": cc,
                        "received": msg['date'],
                        "body": body
                    }
                    }

                    sendTelegram(msg['subject'])
                    sendToRabbit(msg['subject'])

                    resp.set_header('Author-By', '@newbiemember')
                    resp.status = falcon.HTTP_200
                    resp.body = json.dumps(callback, sort_keys=True, indent=2, separators=(',', ': '))
                    conn.close()
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

            conn.curclose()
            conn.close()
        except Exception, e:
            return str(e)


class getEmaildashboard(object):
    def on_post(self, req, resp):
        try:
            if req.get_param('limit') is None:
                rawjson = req.stream.read()
                d = json.loads(rawjson, encoding='utf-8')
                lim = d['limit']
                order = d['order']
            else:
                lim = req.get_param('limit')
                order = req.get_param('order')

            if lim is None:
                data = {'_section': conn.query("select", "select * from email_receive left OUTER join email_tasklist on email_receive.id_email = email_tasklist.id_email ORDER by email_receive.id_email " + order, None)}
            else:
                data = {'_section': conn.query("select", "select * from email_receive left OUTER join email_tasklist on email_receive.id_email = email_tasklist.id_email ORDER by email_receive.id_email " + order + " limit " +lim, None)}

            resp.set_header('Author-By', '@newbiemember')
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(data, default=datetime_handler)


        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Error',
                                   ex.message)

class getTaskEmailID(object):
    def on_post(self, req, resp):
        try:
            if req.get_param('id_email') is None:
                rawjson = req.stream.read()
                data = json.loads(rawjson, encoding='utf-8')
                id_email = data['id_email']
            else:
                id_email = req.get_param('id_email')

            data = {'_section': conn.query("select",
                                           "select * from email_receive where id_email=" + id_email,None)}

            resp.set_header('Author-By', '@newbiemember')
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(data, default=datetime_handler)

        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400,
                               'Error',
                               ex.message)

class sendEmailResponse(object):
    def on_post(self, req, resp):
        try:
            if req.get_param('id_email') is None:

                rawjson = req.stream.read()
                data = json.loads(rawjson, encoding='utf-8')

                id_email = data['id_email']
                body_email = data['body_email']

                if data['status'] == 0:
                    status = 0
                else:
                    status = int(data['status'])
                    keynote = data['keynote']

            else:
                id_email = req.get_param('id_email')
                body_email= req.get_param('body_email')

                if req.get_param('status') == None:
                    status = 0
                else:
                    status = int(req.get_param('status'))
                    keynote = req.get_param('keynote')

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
            getq   = "select id_member, secret from members where username=%s"
            getq   = conn.query("select", getq,username)
            dict   = getq[0]

            secret = dict.get('secret')
            depassword = decryption(password,secret)
            if status == 0:
                sendmail(username, toaddr, cc, subject, body_email, depassword)
                qin = "insert into email_tasklist (id_member,id_email,response) VALUES (%s,%s,now())"
                conn.query("insert", qin, (dict.get('id_member'),id_email))
                callback = {"sendmail": True, "id_member": dict.get('id_member'), "response-by": username, "status": 0, "body_email":body_email }
                resp.set_header('Author-By', '@newbiemember')
                resp.status = falcon.HTTP_200
                resp.body = json.dumps(callback, sort_keys=True, indent=2, separators=(',', ': '))
            elif status == 1:
                sendmail(username, toaddr, cc, subject, body_email, depassword)
                qup = "update email_tasklist set status=%s, keynote=%s, selesai=now() where id_email=%s and status=0"
                conn.query("update", qup, (1, keynote, id_email))
                callback = {"sendmail": True,'id_member': dict.get('id_member'), "finish-by": username, "status": 1, "body_email":body_email, "keynote": keynote}
                resp.set_header('Author-By', '@newbiemember')
                resp.status = falcon.HTTP_200
                resp.body = json.dumps(callback, sort_keys=True, indent=2, separators=(',', ': '))
            else:
                callback = {"sendmail": False}
                resp.set_header('Author-By', '@newbiemember')
                resp.status = falcon.HTTP_200
                resp.body = json.dumps(callback, sort_keys=True, indent=2, separators=(',', ': '))
            conn.curclose()
            conn.close()

        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400,
                               'Error',
                               ex.message)


