import falcon
from GlobalEnvironment.db import DB
import json
conn = DB()

class troubleTask(object):
    def on_post(self, req, resp):
        msg = req.get_param('message')
        msg = msg.split(',')
        subject = msg[0]
        message = msg[1]
        if msg is not None:
            cekquery = "select subject, status from trouble_tasklist where subject=%s"
            cekq = conn.select(cekquery, subject)

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
