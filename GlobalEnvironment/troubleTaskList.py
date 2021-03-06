import falcon
from GlobalEnvironment.db import DB
from GlobalEnvironment.GlobalFunctions import jwtDecode, sendmail
from datetime import datetime
import json
conn = DB()

class troubleTask(object):
    def on_post(self, req, resp):
        try:
            rawjson = req.stream.read()
            data = json.loads(rawjson, encoding='utf-8')

            if req.get_param('message') is None:
                msg = data['message']
            else:
                msg = req.get_param('message')

            msg = msg.split(',')
            subject = msg[0]
            message = msg[1]

            if subject == "dglog-worker":
                sendmail("eddy@codigo.id", "netcj@codigo.id", None, "ALERT " + subject + " " + message,
                         str(datetime.now()),
                         "Cyberl1nk")

            if msg is not None:
                cekquery = "select subject, status from trouble_tasklist where subject=%s"
                cekq = conn.query("select", cekquery, (subject))

                try:
                    dict = cekq[0]
                    status = dict.get('status')
                except Exception:
                    status = None

                if status is None or status == 1:
                    query = "insert into trouble_tasklist(subject, message) VALUES (%s,%s)"
                    conn.query("insert", query, (subject, message))
                    callback = {"inserted": True, "host": subject,"message": message}
                    resp.set_header('Author-By', '@newbiemember')
                    resp.status = falcon.HTTP_200
                    resp.body = json.dumps(callback, sort_keys=True, indent=2, separators=(',', ': '))
                if status == 0:
                    query = "update trouble_tasklist set message=%s where subject=%s"
                    conn.query("update", query, (message, subject))
                    callback = {"update": True, "host": subject, "message": message}
                    resp.set_header('Author-By', '@newbiemember')
                    resp.status = falcon.HTTP_200
                    resp.body = json.dumps(callback, sort_keys=True, indent=2, separators=(',', ': '))
            else:
                callback = {"inserted": False, "error": "empty value"}
                resp.set_header('Author-By', '@newbiemember')
                resp.status = falcon.HTTP_200
                resp.body = json.dumps(callback, sort_keys=True, indent=2, separators=(',', ': '))
            conn.curclose()
            conn.close()

        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Error',
                                   ex.message)

class updateTroubleTask(object):
    def on_post(self,req,resp):
        try:
            rawjson = req.stream.read()
            data = json.loads(rawjson, encoding='utf-8')

            if req.get_param('id') is None:
                id = data['id']
                note = data['note']
            else:
                id = req.get_param('id')
                note = req.get_param('note')

            token = req.get_header('Authorization')
            username,password = jwtDecode(token)

            query = "update trouble_tasklist set status=1, date_released=now(), username=%s, note=%s where id_trouble=%s and status=0"
            conn.query("update", query,(username,note,id))

            callback = {"status": "solved", "by": username, "note": note}
            resp.set_header('Author-By', '@newbiemember')
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(callback, sort_keys=True, indent=2, separators=(',', ': '))
            conn.curclose()
            conn.close()

        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Error',
                                   ex.message)