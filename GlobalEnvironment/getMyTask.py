import falcon
from GlobalEnvironment.db import DB
from GlobalEnvironment.GlobalFunctions import jwtDecode
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

class getMyTask(object):
    def on_post(self, req, resp):
        try:
            rawjson = req.stream.read()
            data = json.loads(rawjson, encoding='utf-8')
            token = req.get_header('Authorization')

            if req.get_param('limit') is None:
                lim = data['limit']
                source = data['source']
            else:
                lim = req.get_param('limit')
                source = req.get_param('source')

            username, password = jwtDecode(token)
            getuser = "select count(id_member) as count, id_member from members WHERE tokenExp=0" \
                      "and username=%s and password=%s"
            datauser = conn.query("select",getuser,(username,password))
            dict = datauser[0]

            if dict.get('count') == 1:
                if lim is None:
                    if source == "email":
                        query = "select * from email_receive left OUTER join " \
                                "email_tasklist on email_receive.id_email = email_tasklist.id_email" \
                                "left OUTER join members on email_tasklist.id_member = members.id_member" \
                                "where username=%s and password=%s and tokenExp=0"
                    if source == "request":
                        query = "select * from submited_tasklist left OUTER JOIN " \
                                "members on submited_tasklist.id_member = members.id_member" \
                                "where username=%s and password=%s and tokenExp=0"
                    if source == "kapacitor":
                        query = "select * from trouble_tasklist left OUTER JOIN " \
                                "members on trouble_tasklist.id_member = members.id_member" \
                                "where username=%s and password=%s and tokenExp=0"

                    data = {source:conn.query("select",query,(username,password))}
                    resp.set_header('Author-By', '@newbiemember')
                    resp.status = falcon.HTTP_200
                    resp.body = json.dumps(data, default=datetime_handler)

                else:
                    if source == "email":
                        query = "select * from email_receive left OUTER join " \
                                "email_tasklist on email_receive.id_email = email_tasklist.id_email" \
                                "left OUTER join members on email_tasklist.id_member = members.id_member" \
                                "where username=%s and password=%s and tokenExp=0 limit "+lim
                    if source == "request":
                        query = "select * from submited_tasklist left OUTER JOIN " \
                                "members on submited_tasklist.id_member = members.id_member" \
                                "where username=%s and password=%s and tokenExp=0 limit "+lim
                    if source == "kapacitor":
                        query = "select * from trouble_tasklist left OUTER JOIN " \
                                "members on trouble_tasklist.id_member = members.id_member" \
                                "where username=%s and password=%s and tokenExp=0 limit "+lim

                    data = {source: conn.query("select", query(username,password))}
                    resp.set_header('Author-By', '@newbiemember')
                    resp.status = falcon.HTTP_200
                    resp.body = json.dumps(data, default=datetime_handler)

            conn.curclose()
            conn.close()
        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Error',
                                   ex.message)