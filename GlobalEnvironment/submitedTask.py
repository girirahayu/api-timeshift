import falcon
from GlobalEnvironment.db import DB
from GlobalEnvironment.GlobalFunctions import jwtDecode
import json
import jwt

JWT_SECRET = 'infra@codigo'
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 20

conn = DB()

class getMembers(object):
    def on_get(self, req, resp):
        data = {'_member': conn.query("select",
                                       "select id_member,tokenExp,username from members",
                                       None)}

        resp.set_header('Author-By', '@newbiemember')
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(data, sort_keys=True, indent=2, separators=(',', ': '))
        conn.curclose()
        conn.close()

class submitTask(object):
    def on_post(self,req, resp):

        try:
            token = req.get_header('Authorization')
            rawjson = req.stream.read()
            data = json.loads(rawjson, encoding='utf-8')
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

            query = "select id_member from members where username=%s and password=%s"
            cek = conn.query("select", query, (payload['username'], payload['password']))
            dict = cek[0]

            nametask = data['nametask']
            desctask = data['desctask']
            note    = data['note']
            id      = dict.get('id_member')

            query = "insert into submited_tasklist(judul_task, desc_task, date_received,id_member,note) VALUES (%s,%s,now(),%s,%s)"
            conn.query("insert", query, (nametask,desctask,id,note))
            callback = {"task": "submited", "nametask": nametask, "status":"saved"}
            resp.set_header('Author-By', '@newbiemember')
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(callback, sort_keys=True, indent=2, separators=(',', ': '))

            conn.curclose()
            conn.close()

        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Error',
                                   ex.message)

class updateTaskStatus(object):
    def on_post(self,req,resp):
        try:
            rawjson = req.stream.read()
            data = json.loads(rawjson, encoding='utf-8')

            if req.get_param('id_task') is None:
                idtask = data['id_task']
                note = data['note']
            else:
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
        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Error',
                                   ex.message)

