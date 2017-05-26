import falcon
from falcon_multipart.middleware import MultipartMiddleware
from GlobalEnvironment.tokenValidate import getToken
import json


class index(object):
    def on_get(self, req, resp):
        data = {'status': 'Ok'}
        resp.set_header('Powered-By', 'Falcon')
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(data, sort_keys=True, indent=2, separators=(',', ': '))

    def on_post(self,req,resp):
        try:
            req.stream.read()
        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Error',
                                   ex.message)
        try:
            data = {'title':'Notification','Description':'You Cant find something in here'}
            resp.set_header('Powered-By', 'Falcon')
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(data, sort_keys=True, indent=2, separators=(',', ': '))

        except ValueError:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Malformed JSON',
                                   'Could not decode the request body. The '
                                   'JSON was incorrect.')

app = falcon.API(middleware=[
    MultipartMiddleware(),
    #AuthMiddleware(),
    #RequireJSON(),
])

app.add_route('/', index())
app.add_route('/getToken', getToken())