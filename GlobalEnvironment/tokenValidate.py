from GlobalEnvironment.emailFunction import GlobalEmail
from GlobalEnvironment.db import DB
from GlobalEnvironment.GlobalFunctions import encryption
#from datetime import datetime, timedelta
import falcon
import jwt
import json

JWT_SECRET = 'infra@codigo'
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 20

getEmail = GlobalEmail()
conn = DB()


class getToken(object):
    def on_post(self,req, resp):
        username = req.get_param('username')
        password = req.get_param('password')

        if getEmail.emailValidation(username, password) == 1:

            enco , secre = encryption(password)
            fil = "select count(username) as count from members where username =%s"
            filter = conn.query("select", fil,(username))
            dict = filter[0]
            if dict.get('count') == 0:
                query = "insert into members (username,password,secret) values(%s,%s,%s)"
                conn.query("insert",query,(username,enco,secre))
                payload = {
                    'username': username,
                    'password': enco
                    #'exp': datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
                }
            else:
                query = "update members set username=%s, password=%s, secret=%s where username=%s"
                conn.query("update", query, (username, enco,secre,username))
                payload = {
                    'username': username,
                    'password': enco
                    # 'exp': datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
                }
                # query = "select password from members where username=%s"
                # dataq = conn.query("select", query,username)
                # dict = dataq[0]
                # payload = {
                #     'username': username,
                #     'password': dict.get('password')
                #     #'exp': datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
                # }

            conn.close_cur()
            jwt_token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
            data = {"token": jwt_token.decode('utf-8')}
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(data, sort_keys=True, indent=2, separators=(',', ': '))
        else:
            data = {"status": "Can't validate Email address!"}
            resp.status = falcon.HTTP_401
            resp.body = json.dumps(data, sort_keys=True, indent=2, separators=(',', ': '))

        conn.close_cur()