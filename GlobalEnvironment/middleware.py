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
        except (jwt.DecodeError, jwt.ExpiredSignatureError):
            data = {'status': 'Token Failed!'}
            resp.set_header('Powered-By', 'Falcon')
            resp.status = falcon.HTTP_400
            resp.body = json.dumps(data, sort_keys=True, indent=2, separators=(',', ': '))

        username = payload['username']
        password = payload['password']

        query = "select count(id_member) as count, username, password from members where username=%s and password=%s"
        cek = conn.query("select", query, (username,password))
        dict = cek[0]

        if dict.get('count') == str(1):
            return True
        else:
            description = ('The provided auth token is not valid. '
                           'Please request a new token and try again.')
            raise falcon.HTTPUnauthorized('Authentication required',
                                          description)

