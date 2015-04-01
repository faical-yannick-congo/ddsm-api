import json

from flask.ext.api import status
import flask as fk

from api import app
from ddsmdb.common.models import ProjectModel
from ddsmdb.common.tools.basic_auth import requires_auth

API_VERSION = 1
API_URL = '/api/v{0}'.format(API_VERSION)

@app.route(API_URL + '/<project_name>/', methods=['GET', 'PUT', 'DELETE'])
@requires_auth
def project(project_name):
    if fk.request.method == 'PUT':
        project, created = ProjectModel.objects.get_or_create(name=project_name, user=fk.g.user)
        if created:
            return fk.make_response('Created project', status.HTTP_201_CREATED)
        else:
            return fk.make_response('Project already exists', status.HTTP_200_OK)
    elif fk.request.method == 'GET':
        project = ProjectModel.objects(name=project_name, user=fk.g.user).first_or_404()
        return fk.Response(project.to_smt_json(fk.request), mimetype='application/json')
    elif fk.request.method == 'DELETE':
        project = ProjectModel.objects(name=project_name, user=fk.g.user).first_or_404()
        project.delete()
        return fk.Response('Project deleted', status.HTTP_200_OK)
