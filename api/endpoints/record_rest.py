import json

from flask.ext.api import status
import flask as fk

from api import app
from ddsmdb.common.models import ProjectModel
from ddsmdb.common.models import RecordModel
from ddsmdb.common.tools.basic_auth import requires_auth

API_VERSION = 1
API_URL = '/api/v{0}'.format(API_VERSION)

@app.route(API_URL + '/<project_name>/<record_label>/', methods=['GET', 'DELETE', 'PUT'])
@requires_auth
def record(project_name, record_label):
    project = ProjectModel.objects(name=project_name, user=fk.g.user).first_or_404()
    if fk.request.method == 'GET':
        recordHead = RecordModel.objects(project=project, label=record_label).first_or_404()
        return fk.Response(recordHead.to_json(), mimetype='application/json')
    elif fk.request.method == 'PUT':
        data = json.loads(fk.request.data)
        record, created = RecordModel.objects.get_or_create(project=project, label=record_label)
        record.update(data)
        return fk.Response('Record updated', status.HTTP_200_OK)
    elif fk.request.method == 'DELETE':
        record = RecordModel.objects(project=project, label=record_label).first_or_404()
        record.delete()
        return fk.Response('Record deleted', status.HTTP_200_OK)

