import falcon
from GlobalEnvironment.db import DB
import jwt
import json

JWT_SECRET = 'infra@codigo'
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 20

conn = DB()
class AuthMiddleware(object):
    def process_request(self, req, resp):
        token = req.get_header('Authorization')
        if token is None:
            raise falcon.HTTPUnauthorized('Auth token required',
                                          href='mailto:infra@codigo.id')

        try:
            payload = jwt.decode(token, JWT_SECRET,algorithms = [JWT_ALGORITHM])
            query = "select count(id_member) as count,username from members where tokenExp=0 and username=%s and password=%s"
            cek = conn.query("select", query, (payload['username'],payload['password']))
            dict = cek[0]


            if dict.get('count') == 1:
                return True
            else:
                description = ('The provided auth token is not valid. '
                               'Please request a new token and try again.')
                raise falcon.HTTPUnauthorized('Authentication required',
                                              description)

        except (jwt.DecodeError, jwt.ExpiredSignatureError):
            description = ('The provided auth token is not valid. '
                                   'Please request a new token and try again.')
            raise falcon.HTTPUnauthorized('Authentication required',
                                                  description)

