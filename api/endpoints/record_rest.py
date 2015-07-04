import json

from flask.ext.api import status
import flask as fk

from api import app, check_access, upload_handler, load_image
from ddsmdb.common.models import UserModel
from ddsmdb.common.models import ProjectModel
from ddsmdb.common.models import RecordModel
from ddsmdb.common.models import RecordBodyModel
from ddsmdb.common.models import ContainerModel
from ddsmdb.common.tools.basic_auth import requires_auth
import traceback
import mimetypes
import boto3


# from flask.ext.stormpath import user

API_VERSION = 1
API_URL = '/api/v{0}/private'.format(API_VERSION)

@app.route(API_URL + '/<api_token>/record/push/<project_name>', methods=['POST'])
def push_record(api_token, project_name):
    current_user = check_access(api_token)
    if current_user is not None:
        if fk.request.method == 'POST':
            # user = UserModel.objects(email=user.email).first_or_404()
            project = ProjectModel.objects(name=project_name, owner=current_user).first_or_404()
            s3_client = boto3.client('s3')
            print s3_client.get_bucket_location(Bucket='ddsm-bucket')

            # label = db.StringField(max_length=300)
            # created_at = db.DateTimeField(default=datetime.datetime.now())
            # updated_at = db.DateTimeField(default=datetime.datetime.now())
            # system = db.DictField() # {''}
            # program = db.DictField() # {'version_control':'git|hg|svn|cvs', 'scope':'local|remote', 'location':'hash|https://remote_version.com/repository_id'}
            # inputs = db.ListField(db.DictField()) # [{}]
            # outputs = db.ListField(db.DictField()) # [{}]
            # dependencies = db.ListField(db.DictField())# [{}]

            if len(project.history) > 0:
                record = RecordModel(project=project, container=ContainerModel.objects.with_id(project.history[-1]))
            else:
                record = RecordModel(project=project)
            record.label=str(record.id)

            if fk.request.data:
                try:
                    data = json.loads(fk.request.data)

                    if len(data.get('inputs',[])) != 0:
                        record.inputs = data.get('inputs',[])
                        del data['inputs']
                    else:
                        record.inputs = []

                    if len(data.get('outputs',[])) != 0:
                        record.outputs = data.get('outputs',[])
                        del data['outputs']
                    else:
                        record.outputs = []

                    if len(data.get('dependencies',[])) != 0:
                        record.dependencies = data.get('dependencies',[])
                        del data['dependencies']
                    else:
                        record.dependencies = []

                    if len(data.get('system',{})) != 0:
                        record.system = data.get('system',{})
                        del data['system']
                    else:
                        record.system = {}

                    if len(data.get('program',{})) != 0:
                        record.program = data.get('program',{})
                        del data['program']
                    else:
                        record.program = {}

                    if data.get('status','unknown') != 'unknown':
                        record.status = data.get('status','unknown')
                        del data['status']
                    else:
                        record.status = 'unknown'

                    record.update(data)
                    return fk.Response(str(record.id), status.HTTP_201_CREATED)
                except Exception, e:
                    return fk.make_response(str(traceback.print_exc()), status.HTTP_400_BAD_REQUEST)
            else:
                return fk.make_response('No metadata provided.', status.HTTP_204_NO_CONTENT)
            # if fk.request.files:
            #     try:
            #         if fk.request.files['data']:
            #             data_obj = fk.request.files['data']
            #             data = json.loads(data_obj.read())

            #             if len(data.get('image',[])) != 0:
            #                 record.image = data.get('image',[])
            #                 del data['image']
            #             else:
            #                 record.image = {}
            #             print "Record Image: "+str(record.image)

            #             if len(data.get('signature',{})) != 0:
            #                 record.signature = data.get('signature',{})
            #                 del data['signature']
            #             else:
            #                 record.signature = {}
            #             print "Record Signature: "+str(record.signature)
            #             record.update(data)
            #     except:
            #         pass
            #     # if len(record.image) == 0:
            #     #     print "Image to record..."
            #     try:
            #         if fk.request.files['docker']:
            #             image_obj = fk.request.files['docker']
            #             try: 
            #                 record.save()
            #                 upload_handler(current_user, record, image_obj, 'docker')
            #                 print str(record.image)
            #             except Exception, e:
            #                 traceback.print_exc()
            #                 print "Uploading docker image failed!"

            #         if fk.request.files['binary']:
            #             image_obj = fk.request.files['binary']
            #             try: 
            #                 record.save()
            #                 upload_handler(current_user, record, image_obj, 'binary')
            #                 print str(record.image)
            #             except Exception, e:
            #                 traceback.print_exc()
            #                 print "Uploading executable image failed!"

            #         if fk.request.files['source']:
            #             image_obj = fk.request.files['source']
            #             try: 
            #                 record.save()
            #                 upload_handler(current_user, record, image_obj, 'source')
            #                 print str(record.image)
            #             except Exception, e:
            #                 traceback.print_exc()
            #                 print "Uploading source image failed!"
            #     except:
            #         pass
            #     # else:
            #     #     print "Remote link provided."

            #     # if len(record.signature) == 0:
            #     #     print "Signature to record..."
            #     try:
            #         if fk.request.files['signature']:
            #             signature_obj = fk.request.files['signature']
            #             try: 
            #                 record.save()
            #                 upload_handler(current_user, record, signature_obj, 'signature')
            #                 print str(record.signature)
            #             except Exception, e:
            #                 traceback.print_exc()
            #                 print "Uploading signature failed!"
            #     except:
            #         pass
            #     # else:
            #     #     print "Remote link provided."
            # return fk.Response(str(record.id), status.HTTP_201_CREATED)
        else:
            return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)
    else:
        return fk.Response('Unauthorized api token.', status.HTTP_401_UNAUTHORIZED)

# @app.route(API_URL + '/<api_token>/raw/push/<project_name>', methods=['POST'])
# def push_raw(api_token, project_name):
#     current_user = check_access(api_token)
#     if current_user is not None:
#         if fk.request.method == 'POST':
#             # user = UserModel.objects(email=user.email).first_or_404()
#             project, created = ProjectModel.objects.get_or_create(name=project_name, owner=current_user)
#             record = RecordModel(project=project)
#             # record.save()

#             record.label=str(record.id)
#             record.status="started"
#             record.reason="No reason specified."
#             record.outcome="No outcome expected."

#             print record.label
#             print record.status

#             # if created:
#             if fk.request.data:
#                 try:
#                     data = json.loads(fk.request.data)
#                     if created:
#                         project.private = data.get('private', project.private)
#                         project.status = {'origin':"root"}
#                         project.description = data.get('description', "No description provided.")
#                         project.readme = data.get('readme', "No readme content to show.")
#                         del data['private']
#                         del data['status']
#                         del data['description']
#                         del data['readme']
#                         project.save()
        
#                     if len(data.get('image',[])) != 0:
#                         record.image = data.get('image',[])
#                         del data['image']
#                     else:
#                         record.image = {}
#                     print "Record Image: "+str(record.image)

#                     if len(data.get('signature',{})) != 0:
#                         record.signature = data.get('signature',{})
#                         del data['signature']
#                     else:
#                         record.signature = {}
#                     print "Record Signature: "+str(record.signature)

#                     record.update(data)

#                     print record.label
#                     print record.status
#                 except:
#                     print "No json data provided."

#             if fk.request.files:
#                 try:
#                     if fk.request.files['data']:
#                         data_obj = fk.request.files['data']
#                         data = json.loads(data_obj.read())

#                         if len(data.get('image',[])) != 0:
#                             record.image = data.get('image',[{}])
#                             del data['image']
#                         else:
#                             record.image = {}
#                         print "Record Image: "+str(record.image)

#                         if len(data.get('signature',{})) != 0:
#                             record.signature = data.get('signature',{})
#                             del data['signature']
#                         else:
#                             record.signature = {}
#                         print "Record Signature: "+str(record.signature)
#                         record.update(data)
#                 except:
#                     pass

#                 # if len(record.image) == 0:
#                 #     try:
#                 #         if fk.request.files['image']:
#                 #             image_obj = fk.request.files['image']
#                 #             try: 
#                 #                 record.save()
#                 #                 upload_handler(current_user, record, image_obj, 'record')
#                 #             except Exception, e:
#                 #                 traceback.print_exc()
#                 #                 print "Uploading image failed!"
#                 #     except Exception, e:
#                 #         traceback.print_exc()
#                 # else:
#                 #     print "Remote link provided."

#                 if fk.request.files['docker']:
#                     image_obj = fk.request.files['docker']
#                     try: 
#                         record.save()
#                         upload_handler(current_user, record, image_obj, 'docker')
#                         print str(record.image)
#                     except Exception, e:
#                         traceback.print_exc()
#                         print "Uploading docker image failed!"

#                 if fk.request.files['binary']:
#                     image_obj = fk.request.files['binary']
#                     try: 
#                         record.save()
#                         upload_handler(current_user, record, image_obj, 'binary')
#                         print str(record.image)
#                     except Exception, e:
#                         traceback.print_exc()
#                         print "Uploading executable image failed!"

#                 if fk.request.files['source']:
#                     image_obj = fk.request.files['source']
#                     try: 
#                         record.save()
#                         upload_handler(current_user, record, image_obj, 'source')
#                         print str(record.image)
#                     except Exception, e:
#                         traceback.print_exc()
#                         print "Uploading source image failed!"

#                 # if len(record.signature) == 0:
#                 try:
#                     if fk.request.files['signature']:
#                         signature_obj = fk.request.files['signature']
#                         try: 
#                             record.save()
#                             upload_handler(current_user, record, signature_obj, signature)
#                         except Exception, e:
#                             traceback.print_exc()
#                             print "Uploading signature failed!"
#                 except Exception, e:
#                     traceback.print_exc()
#                 # else:
#                 #     print "Remote link provided."
#             return fk.Response(str(record.id), status.HTTP_201_CREATED)
#         else:
#             return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)
#     else:
#         return fk.Response('Unauthorized api token.', status.HTTP_401_UNAUTHORIZED)

@app.route(API_URL + '/<api_token>/record/sync/<project_name>/<record_id>', methods=['PUT'])
def sync_record(api_token, project_name, record_id):
    current_user = check_access(api_token)
    if current_user is not None:
        if fk.request.method == 'PUT':
            # user = UserModel.objects(email=user.email).first_or_404()
            project = ProjectModel.objects(name=project_name, owner=current_user).first_or_404()
            record = RecordModel.objects.with_id(record_id)
            print "In sync..."
            if record.project == project:
                if fk.request.data:
                    data = json.loads(fk.request.data)

                    if data.get('status','unknown') != 'unknown':
                        record.status = data.get('status','unknown')
                        del data['status']
                    else:
                        record.status = 'unknown'

                    if len(data.get('inputs',[])) != 0:
                        for inp in data.get('inputs',[]):
                            already = False

                            for current in record.inputs:
                                if cmp(current, inp) == 0:
                                    already = True
                                    break

                            if not already:
                                record.inputs.append(inp)
                        del data['inputs']

                    if len(data.get('outputs',[])) != 0:
                        for out in data.get('outputs',[]):
                            already = False

                            for current in record.outputs:
                                if cmp(current, out) == 0:
                                    already = True
                                    break

                            if not already:
                                record.outputs.append(out)
                        del data['outputs']

                    if len(data.get('dependencies',[])) != 0:
                        for dep in data.get('dependencies',[]):
                            already = False

                            for current in record.dependencies:
                                if cmp(current, dep) == 0:
                                    already = True
                                    break

                            if not already:
                                record.dependencies.append(dep)
                        del data['dependencies']

                    if len(data.get('system',{})) != 0:
                        record.system = data.get('system',{})
                        del data['system']

                    if len(data.get('program',{})) != 0:
                        record.program = data.get('program',{})
                        del data['program']

                    record.update(data)
                if fk.request.files:
                    try:
                        if fk.request.files['data']:
                            data_obj = fk.request.files['data']
                            data = json.loads(data_obj.read())

                            if data.get('status','unknown') != 'unknown':
                                record.status = data.get('status','unknown')
                                del data['status']
                            else:
                                record.status = 'unknown'

                            if len(data.get('inputs',[])) != 0:
                                for inp in data.get('inputs',[]):
                                    already = False

                                for current in record.inputs:
                                    if cmp(current, inp) == 0:
                                        already = True
                                        break

                                if not already:
                                    record.inputs.append(inp)
                                del data['inputs']

                            if len(data.get('outputs',[])) != 0:
                                for out in data.get('outputs',[]):
                                    already = False

                                for current in record.outputs:
                                    if cmp(current, out) == 0:
                                        already = True
                                        break

                                if not already:
                                    record.outputs.append(out)
                                del data['outputs']

                            if len(data.get('dependencies',[])) != 0:
                                for dep in data.get('dependencies',[]):
                                    already = False

                                for current in record.dependencies:
                                    if cmp(current, dep) == 0:
                                        already = True
                                        break

                                if not already:
                                    record.dependencies.append(dep)
                                del data['dependencies']

                            if len(data.get('system',{})) != 0:
                                record.system = data.get('system',{})
                                del data['system']

                            if len(data.get('program',{})) != 0:
                                record.program = data.get('program',{})
                                del data['program']

                            record.update(data)
                    except:
                        pass
                    #To handle source code versioning ourself in case.
                    # try:
                    #     if fk.request.files['src']:
                    #         src_obj = fk.request.files['src']
                    #         try: 
                    #             record.save()
                    #             upload_handler(current_user, record, src_obj, 'record')
                    #             print str(record.src)
                    #         except Exception, e:
                    #             traceback.print_exc()
                    #             print "Uploading image failed!"
                    # except:
                    #     pass
                return fk.Response("Record synchronized.", status.HTTP_201_CREATED)
            else:
                return fk.Response("Record sync rejected.", status.HTTP_401_UNAUTHORIZED)
    else:
        return fk.Response('Unauthorized api token.', status.HTTP_401_UNAUTHORIZED)

#Delete this if the pull with the / at the end really pulls all the project activity.
@app.route(API_URL + '/<api_token>/record/pull/<project_name>', methods=['GET'])
def pull_record_all(api_token, project_name):
    current_user = check_access(api_token)
    if current_user is not None:
        if fk.request.method == 'GET':
            project = ProjectModel.objects(name=project_name, owner=current_user).first_or_404()
            records = [json.loads(record.summary_json()) for record in RecordModel.objects(project=project)]
            return fk.Response(json.dumps({'project':project.to_json(), 'records':records}), mimetype='application/json')
        else:
            return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)
    else:
        return fk.Response('Unauthorized api token.', status.HTTP_401_UNAUTHORIZED)

# @app.route(API_URL + '/<api_token>/<user_id>/record/clone/<project_name>/<record_id>', methods=['GET'])
# def clone_record(api_token, user_id, project_name, record_id):
#     current_user = check_access(api_token)
#     if current_user is not None:
#         if fk.request.method == 'GET':
#             owner = UserModel.objects(id=user_id).first_or_404()
#             project = ProjectModel.objects(name=project_name, owner=owner).first_or_404()
#             if not project.private:
#                 record = RecordModel.objects.with_id(record_id)
#                 clo_project = ProjectModel.objects(name=project_name, owner=current_user).first()
#                 if clo_project == None:
#                     clo_project = project.clone()
#                     clo_project.user = current_user
#                     clo_project.status = {'origin':str(user_id)+":"+project_name+":"+str(record_id)}
#                     clo_project.save()
#                 clo_record = RecordModel.objects.with_id(record_id)
#                 if clo_record == None or (clo_record != None and clo_record.project != clo_project):
#                     clo_record = record.clone()
#                     clo_record.project = clo_project
#                     clo_record.save()
#                     return fk.Response("Record cloned.", status.HTTP_201_CREATED)
#                 else:
#                     return fk.Response("Record already cloned!", status.HTTP_201_CREATED)
#             else:
#                 return fk.make_response('Access denied. Private project.', status.HTTP_401_UNAUTHORIZED)
#         else:
#             return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)
#     else:
#         return fk.Response('Unauthorized api token.', status.HTTP_401_UNAUTHORIZED)

@app.route(API_URL + '/<api_token>/record/display/<project_name>/<record_id>', methods=['GET'])
def pull_record_single(api_token, project_name, record_id):
    current_user = check_access(api_token)
    if current_user is not None:
        if fk.request.method == 'GET':
            # user = UserModel.objects(email=user.email).first_or_404()
            record = RecordModel.objects.with_id(record_id)
            project = ProjectModel.objects.with_id(record.project.id)
            if (project.private and (project.owner == current_user)) or (not project.private):
                if record_id is not None:
                    return fk.Response(record.to_json(), mimetype='application/json')
                else:
                    project = ProjectModel.objects(name=project_name, owner=current_user).first_or_404()
                    records = [json.loads(record.summary_json()) for record in RecordModel.objects(project=project)]
                    return fk.Response(json.dumps({'project':project.to_json(), 'records':records}), mimetype='application/json')
            else:
                return fk.Response('Record pull rejected.', status.HTTP_401_UNAUTHORIZED)
        else:
            return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)
    else:
        return fk.Response('Unauthorized api token.', status.HTTP_401_UNAUTHORIZED)

@app.route(API_URL + '/<api_token>/record/pull/<project_name>/<record_id>', methods=['GET'])
def pull_record(api_token, project_name, record_id):
    current_user = check_access(api_token)
    if current_user is not None:
        if fk.request.method == 'GET':
            # user = UserModel.objects(email=user.email).first_or_404()
            record = RecordModel.objects.with_id(record_id)
            project = ProjectModel.objects.with_id(record.project.id)
            if (project.private and (project.owner == current_user)) or (not project.private):
                if record_id is not None:
                    if record.container:
                        container = record.container
                        if container.image['location']:
                            image = load_image(container)
                            print image[1]
                            return fk.send_file(
                                image[0],
                                mimetypes.guess_type(image[1])[0],
                                as_attachment=True,
                                attachment_filename=str(current_user.id)+"-"+project_name+"-"+str(record_id)+"-record.tar",
                            )
                        else:
                            return fk.make_response('Empty location. Nothing to pull from here!', status.HTTP_204_NO_CONTENT)
                    else:
                        return fk.make_response('No container image. Nothing to pull from here!', status.HTTP_204_NO_CONTENT)
                else:
                    return fk.make_response('Nothing to pull from here!', status.HTTP_204_NO_CONTENT)
            else:
                return fk.Response('Record pull rejected.', status.HTTP_401_UNAUTHORIZED)
        else:
            return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)
    else:
        return fk.Response('Unauthorized api token.', status.HTTP_401_UNAUTHORIZED)

#Delete this if the one remove with / at the end really delete all the records.
# @app.route(API_URL + '/<api_token>/record/remove/<project_name>', methods=['DELETE'])
# def remove_all_record(api_token, project_name):
#     current_user = check_access(api_token)
#     if current_user is not None:
#         if fk.request.method == 'DELETE':
#             # user = UserModel.objects(email=user.email).first_or_404()
#             project = ProjectModel.objects(name=project_name, owner=current_user).first_or_404()
#             records = RecordModel.objects(project=project)
#             for record in records:
#                 record.delete()
#             return fk.Response("All records deleted.", status.HTTP_201_CREATED)
#         else:
#             return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)
#     else:
#         return fk.Response('Unauthorized api token.', status.HTTP_401_UNAUTHORIZED)

# @app.route(API_URL + '/<api_token>/record/remove/<project_name>/<record_id>', methods=['DELETE'])
# def remove_record(api_token, project_name, record_id):
#     current_user = check_access(api_token)
#     if current_user is not None:
#         if fk.request.method == 'DELETE':
#             # user = UserModel.objects(email=user.email).first_or_404()
#             project = ProjectModel.objects(name=project_name, owner=current_user).first_or_404()
#             record = RecordModel.objects.with_id(record_id)
#             if record.project == project:
#                 if record_id is not None:
#                     record.delete()
#                     return fk.Response("Record deleted.", status.HTTP_201_CREATED)
#                 else:
#                     records = RecordModel.objects(project=project)
#                     for record in records:
#                         record.delete()
#                     return fk.Response("All records deleted.", status.HTTP_201_CREATED)
#             else:
#                 return fk.Response("Record delete rejected.", status.HTTP_401_UNAUTHORIZED)
#         else:
#             return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)
#     else:
#         return fk.Response('Unauthorized api token.', status.HTTP_401_UNAUTHORIZED)

# @app.route(API_URL + '/<api_token>/record/dashboard/<project_name>', methods=['GET'])
# def dashboard_record(api_token, project_name):
#     current_user = check_access(api_token)
#     if current_user is not None:
#         if fk.request.method == 'GET':
#             project = ProjectModel.objects(name=project_name, owner=current_user).first_or_404()
#             records = [json.loads(record.summary_json()) for record in RecordModel.objects(project=project)]
#             return fk.Response(json.dumps({'project':project.to_json(), 'records':records}), mimetype='application/json')
#         else:
#             return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)
#     else:
#         return fk.Response('Unauthorized api token.', status.HTTP_401_UNAUTHORIZED)