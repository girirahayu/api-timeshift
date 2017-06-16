import falcon
from falcon_multipart.middleware import MultipartMiddleware
from GlobalEnvironment.tokenValidate import getToken
from GlobalEnvironment.emailFunction import getEmail, sendEmailResponse, getEmaildashboard
from GlobalEnvironment.middleware import AuthMiddleware
from GlobalEnvironment.troubleTaskList import troubleTask, updateTroubleTask
from GlobalEnvironment.submitedTask import submitTask, updateTaskStatus
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
])

app.add_route('/', index())
app.add_route('/getToken', getToken())
app.add_route('/getEmail', getEmail())
app.add_route('/getTaskEmailDashboard', getEmaildashboard())
app.add_route('/sendEmailResponse', sendEmailResponse())
app.add_route('/troubleTask', troubleTask())
app.add_route('/updateTroubleTask', updateTroubleTask())
app.add_route('/submitTask', submitTask())
app.add_route('/updateTask', updateTaskStatus())
