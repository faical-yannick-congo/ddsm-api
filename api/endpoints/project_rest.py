import json

from flask.ext.api import status
import flask as fk

from api import app, check_access, upload_handler
from ddsmdb.common.models import ProjectModel
from ddsmdb.common.models import ContainerModel
from ddsmdb.common.models import UserModel
from ddsmdb.common.models import RecordModel

import mimetypes

import traceback

# from flask.ext.stormpath import user

API_VERSION = 1
API_URL = '/api/v{0}/private'.format(API_VERSION)

@app.route(API_URL + '/<api_token>/project/push/<project_name>', methods=['POST'])
def push_project(api_token, project_name):
    print api_token
    current_user = check_access(api_token)
    if current_user is not None:
        # user = UserModel.objects(email=user.email).first_or_404()
        if fk.request.method == 'POST': # POST to create a new one only.
            project, created = ProjectModel.objects.get_or_create(name=project_name, owner=current_user)

            if created:

                # created_at = db.DateTimeField(default=datetime.datetime.now())
                # owner = db.ReferenceField(UserModel, reverse_delete_rule=db.CASCADE, required=True)
                # name = db.StringField(max_length=300, required=True)
                # description = db.StringField(max_length=10000)
                # goals = db.StringField(max_length=500)
                # private = db.BooleanField(default=False)
                # history = db.ListField(db.EmbeddedDocumentField(ContainerModel))

                project.description = 'No description provided.'
                project.goals = 'No goals provided.'
                if fk.request.data:
                    data = json.loads(fk.request.data)
                    project.private = data.get('private', False)
                    project.description = data.get('description', project.description)
                    project.goals = data.get('goals', project.goals)

                project.save()

                return fk.make_response("Project created.", status.HTTP_201_CREATED)
            else:
                return fk.make_response('Push refused. Project name already used.', status.HTTP_401_UNAUTHORIZED)
        else:
            return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)
    else:
        return fk.make_response('Unauthorized api token.', status.HTTP_401_UNAUTHORIZED)


@app.route(API_URL + '/<api_token>/project/sync/<project_name>', methods=['PUT', 'POST'])
def sync_project(api_token, project_name):
    current_user = check_access(api_token)
    if current_user is not None:
        # user = UserModel.objects(email=user.email).first_or_404()
        if fk.request.method == 'PUT': # PUT to update an existing one only.
            project = ProjectModel.objects(name=project_name, owner=current_user).first_or_404()
            if fk.request.data:
                data = json.loads(fk.request.data)
                project.name = data.get('name', project.name)
                project.private = data.get('private', project.private)
                project.description = data.get('description', project.description)
                project.goals = data.get('goals', project.goals)
            project.save()
            return fk.make_response('Project synchronized.', status.HTTP_201_CREATED)
        elif fk.request.method == 'POST':
            project = ProjectModel.objects(name=project_name, owner=current_user).first_or_404()
            container = ContainerModel()
            if fk.request.files:
                print "Contains some request files..."
                try:
                    if fk.request.files['data']:
                        data_obj = fk.request.files['data']
                        data = json.loads(data_obj.read())
                        print str(data)
                        containing = {}
                        if data.get('system','unknown') != 'unknown':
                            container.system = data.get('system', 'unknown')
                            del data['system']
                        else:
                            container.system = 'unknown'
                        print "Project Container System: "+str(container.system)

                        if len(data.get('version',{})) != 0:
                            container.version = data.get('version',{})
                            del data['version']
                        else:
                            container.version = {}
                        print "Project Version Control: "+str(container.version)

                        if len(data.get('image',{})) != 0:
                            container.image = data.get('image',{'scope':'unknown'})
                            del data['image']
                        else:
                            container.image = {'scope':'unknown'} # unknown, local, remote
                        print "Project Image Scope: "+str(container.image)
                        container.save()
                except Exception, e:
                    return fk.make_response(str(traceback.print_exc()), status.HTTP_400_BAD_REQUEST)
                # if len(record.image) == 0:
                #     print "Image to record..."
                if container.image['scope'] == 'local':
                    try:
                        if fk.request.files['image']:
                            image_obj = fk.request.files['image']
                            try: 
                                container.save()
                                upload_handler(current_user, container, image_obj, container.system)
                                project.history.append(str(container.id))
                                project.save()
                                print str(project.history[-1])
                            except Exception, e:
                                return fk.make_response(str(traceback.print_exc()), status.HTTP_400_BAD_REQUEST)
                    except Exception, e:
                        return fk.make_response(str(traceback.print_exc()), status.HTTP_400_BAD_REQUEST)
                return fk.make_response('Project is at the new staged container image.', status.HTTP_201_CREATED)
            else:
                return fk.make_response('No container image staged here.', status.HTTP_204_NO_CONTENT)
        else:
            return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)
    else:
        return fk.make_response('Unauthorized api token.', status.HTTP_401_UNAUTHORIZED)

# @app.route(API_URL + '/<api_token>/<user_id>/project/clone/<project_name>', methods=['GET'])
# def clone_project(api_token, user_id, project_name):
#     current_user = check_access(api_token)
#     if current_user is not None:
#         if fk.request.method == 'GET':
#             owner = UserModel.objects(id=user_id).first_or_404()
#             project = ProjectModel.objects(name=project_name, owner=owner).first_or_404()
#             if not project.private:
#                 clo_project = ProjectModel.objects(name=project_name, owner=current_user).first()
#                 if clo_project == None:
#                     clo_project = project.clone()
#                     clo_project.owner = current_user
#                     clo_project.status = {'origin':str(user_id)+":"+project_name+":"+str(record_id)}
#                     clo_project.save()
#                 else:
#                     return fk.Response("Project already exist in your workspace!", status.HTTP_201_CREATED)
#             else:
#                 return fk.make_response('Access denied. Private project.', status.HTTP_401_UNAUTHORIZED)
#         else:
#             return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)
#     else:
#         return fk.Response('Unauthorized api token.', status.HTTP_401_UNAUTHORIZED)

@app.route(API_URL + '/<api_token>/project/pull', methods=['GET'])
def pull_project_all(api_token):
    current_user = check_access(api_token)
    if current_user is not None:
        if fk.request.method == 'GET':
            projects = ProjectModel.objects(owner=current_user)
            summaries = sorted([json.loads(p.summary_json()) for p in projects], key = lambda project: prject['created'])
            # summaries = [json.loads(p.summary_json()) for p in projects]
            return fk.Response(json.dumps({'number':len(summaries), 'projects':summaries}), mimetype='application/json')
        else:
            return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)
    else:
        return fk.make_response('Unauthorized api token.', status.HTTP_401_UNAUTHORIZED)

@app.route(API_URL + '/<api_token>/project/pull/<project_name>', methods=['GET'])
def pull_project(api_token, project_name):
    current_user = check_access(api_token)
    if current_user is not None:
        if fk.request.method == 'GET':
            # user = UserModel.objects(email=user.email).first_or_404()
            if project_name is not None:
                project = ProjectModel.objects(owner=current_user, name=project_name).first_or_404()
                return fk.Response(project.activity_json(), mimetype='application/json')
            # else:
            #     projects = ProjectModel.objects(owner=current_user)
            #     summaries = [p.summary_json() for p in projects]
            #     return fk.Response(json.dumps({'projects':summaries}), mimetype='application/json')
        else:
            return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)
    else:
        return fk.make_response('Unauthorized api token.', status.HTTP_401_UNAUTHORIZED)

@app.route(API_URL + '/<api_token>/project/remove/<project_name>', methods=['DELETE'])
def remove_project(api_token, project_name):
    current_user = check_access(api_token)
    if current_user is not None:
        if fk.request.method == 'DELETE':
            # user = UserModel.objects(email=user.email).first_or_404()
            if project_name is not None:
                project = ProjectModel.objects(name=project_name, owner=current_user).first_or_404()
                project.delete()
                return fk.Response('Project deleted', status.HTTP_200_OK)
            else:
                projects = ProjectModel.objects(owner=current_user)
                for project in projects:
                    project.delete()
                return fk.Response('All projects deleted', status.HTTP_200_OK)
        else:
            return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)
    else:
        return fk.make_response('Unauthorized api token.', status.HTTP_401_UNAUTHORIZED)


@app.route(API_URL + '/<api_token>/project/dashboard', methods=['GET'])
def dashboard_project(api_token):
    current_user = check_access(api_token)
    if current_user is not None:
        if fk.request.method == 'GET':
            projects = ProjectModel.objects(owner=current_user)
            summaries = []
            for p in projects:
                project = {"project":p.summary_json()}
                records = RecordModel.pbjects(project=p)
                project["activity"] = {"number":len(records), "records":[{"id":record.id, "created":record.created_at} for record in records]}
                summaries.append(project)
            return fk.Response(json.dumps({'number':len(summaries), 'projects':summaries}), mimetype='application/json')
        else:
            return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)
    else:
        return fk.make_response('Unauthorized api token.', status.HTTP_401_UNAUTHORIZED)