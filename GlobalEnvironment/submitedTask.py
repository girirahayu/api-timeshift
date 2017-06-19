import falcon
from GlobalEnvironment.db import DB
from GlobalEnvironment.GlobalFunctions import jwtDecode
import json
conn = DB()

class submitTask(object):
    def on_post(self,req, resp):
        nametask = req.get_param('nametask')
        desctask = req.get_param('desctask')
        username = req.get_param('to')

        if nametask or desctask or username is not None:
            query = "insert into submited_tasklist(judul_task, desc_task, username) VALUES (%s,%s,%s)"
            conn.query("insert", query, (nametask,desctask,username))
            callback = {"task": "submited", "to": username, "nametask": nametask, "status":"delivered"}
            resp.set_header('Author-By', '@newbiemember')
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(callback, sort_keys=True, indent=2, separators=(',', ': '))
        conn.curclose()
        conn.close()

class updateTaskStatus(object):
    def on_post(self,req,resp):
        idtask = req.get_param('id_task')
        note = req.get_param('note')

        token = req.get_header('Authorization')
        username,password = jwtDecode(token)
        #get secret from database for decript password:

        getUser = "select username as user from submited_tasklist where id_task=%s"
        conn.query("select",idtask)
        dict   = getUser[0]
        user = dict.get('user')

        if user == username:
            query = "update submited_tasklist set status=1, date_released=now(), note=%s where id_task=%s and status=0"
            conn.query("update", query, (note, idtask))
            callback = {"task": "submited", "status": "solved", "note": note}
            resp.set_header('Author-By', '@newbiemember')
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(callback, sort_keys=True, indent=2, separators=(',', ': '))
        else:
            callback = {"task": "unsubmited", "status": "fail", "note": "you don't have privilege to change status this case!"}
            resp.set_header('Author-By', '@newbiemember')
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(callback, sort_keys=True, indent=2, separators=(',', ': '))

        conn.curclose()
        conn.close()

