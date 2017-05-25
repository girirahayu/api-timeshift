import json
from datetime import datetime, timedelta
from aiohttp import web
from GlobalEnvironment.emailFunction import GlobalEmail
import jwt

JWT_SECRET = 'infra@codigo'
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 20
getEmail = GlobalEmail()

def json_response(body='', **kwargs):
    kwargs['body'] = json.dumps((body or kwargs['body']), sort_keys=True, indent=2, separators=(',', ': ')).encode('utf-8')
    kwargs['content_type'] = 'text/json'
    return web.Response(**kwargs)

async def auth(request):
    post = await request.post()
    email   = post['email']
    password= post['password']
    if getEmail.emailValidation(email,password) == 1:
        payload = {
            'email': email,
            'password': password
            #if need using expire time
            #'exp': datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
        }
        jwt_token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
        return json_response({'token': jwt_token.decode('utf-8')})
    else:
        return json_response({'message': 'Wrong credentials'}, status=400)


async def index(request):
    return json_response({'user': str(request.user)})

async def middleware(app, handler):
    async def middleware(request):
        request.user = None
        token = request.headers.get('authorization', None)
        if token:
            try:
                payload = jwt.decode(token, JWT_SECRET,
                                     algorithms=[JWT_ALGORITHM])
            except (jwt.DecodeError, jwt.ExpiredSignatureError):
                return json_response({'message': 'Token is invalid'}, status=400)

            request.user = payload['email']

        return await handler(request)
    return middleware

app = web.Application(middlewares=[middleware])
app.router.add_route('POST','/login', auth)
app.router.add_route('GET','/', index)



