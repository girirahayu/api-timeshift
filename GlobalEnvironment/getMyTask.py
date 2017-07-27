import falcon
from GlobalEnvironment.db import DB
import jwt
JWT_SECRET = 'infra@codigo'
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 20

import json
conn = DB()
import datetime

def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    raise TypeError("Unknown type")

class myDashboardList(object):
    def on_post(self, req, resp):

        try:
            token = req.get_header('Authorization')
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

            rawjson = req.stream.read()
            data = json.loads(rawjson, encoding='utf-8')

            limit = data['limit']
            order = data['order']
            source= data['sourceTask']
            username = payload['username']
            print limit

            if "email" in source:
                call = {'_email': conn.query("select",
                                             "select er.* , et.*, m.username from email_receive er , email_tasklist et, members m where er.id_email=et.id_email and et.id_member = m.id_member and m.username='"+username+"' order by er.id_email "+ order + " limit " +limit, None)}

                resp.set_header('Author-By', '@newbiemember')
                resp.status = falcon.HTTP_200
                resp.body = json.dumps(call, default=datetime_handler)

        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400,
                               'Error',
                               ex.message)