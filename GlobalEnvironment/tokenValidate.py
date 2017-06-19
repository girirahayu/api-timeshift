from GlobalEnvironment.emailFunction import GlobalEmail
from GlobalEnvironment.db import DB
from GlobalEnvironment.GlobalFunctions import encryption
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
                }
            else:
                query = "update members set tokenExp=0, username=%s, password=%s, secret=%s where username=%s"
                conn.query("update", query, (username, enco,secre,username))
                payload = {
                    'username': username,
                    'password': enco
                }

            jwt_token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
            data = {"token": jwt_token.decode('utf-8')}
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(data, sort_keys=True, indent=2, separators=(',', ': '))
        else:
            data = {"status": "Can't validate Email address!"}
            resp.status = falcon.HTTP_401
            resp.body = json.dumps(data, sort_keys=True, indent=2, separators=(',', ': '))
        conn.curclose()
        conn.close()


class disableToken(object):
    def on_get(self, req, resp):
        token = req.get_header('Authorization')
        
        try:
            payload = jwt.decode(token, JWT_SECRET,algorithms = [JWT_ALGORITHM])
            query = "select count(id_member) as count from members where tokenExp=0 and username=%s and password=%s"
            cek = conn.query("select", query, (payload['username'],payload['password']))
            dict = cek[0]

            if dict.get('count') == 1:
                update = "update members set tokenExp=1 where username=%s and password=%s"
                conn.query("update", update,(payload['username'],payload['password']))
                data = {"user": payload['username'], "signout": True}
                resp.status = falcon.HTTP_200
                resp.body = json.dumps(data, sort_keys=True, indent=2, separators=(',', ': '))
            conn.curclose()
            conn.close()
        except (jwt.DecodeError, jwt.ExpiredSignatureError):
            description = ('Your token has expired '
                       'Please request a new token and try again.')
            raise falcon.HTTPUnauthorized('Authentication required',
                                      description)