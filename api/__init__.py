# The api module
from ddsmdb.common.core import setup_app
from ddsmdb.common.models import UserModel
from ddsmdb.common.models import ProjectModel        
import tempfile
import tarfile
from StringIO import StringIO
import os
import json
import difflib
import hashlib
import datetime
import boto3
import traceback
# from difflib_data import *

app = setup_app(__name__)

s3 =  boto3.resource('s3')


from flask.ext.stormpath import StormpathManager

stormpath_manager = StormpathManager(app)

def check_access(token):
    # for account in stormpath_manager.client.accounts:
    	# if account.custom_data.get('token') == token:
    # if token == "abcdefghijklmnopqrst0123456789":
    # 	return UserModel.objects.first_or_404()
    # else:
    # 	return None
    for user in UserModel.objects():
        print "%s -- %s." %(user.email, user.api_token)
    return UserModel.objects(api_token=token).first()

# def docker_gen(current_user, project):
#     docker_tar = tarfile.open("/tmp/"+str(current_user.id)+"-"+project.name+"-docker.tar", "w")
#     # print project.docker
#     # print project.requirements
#     if project.docker != "":
#         dockerfile = open("/tmp/"+str(current_user.id)+"-"+project.name+"-Dockerfile", "w")
#         dockerfile.write(project.docker)
#         dockerfile.close()
#         docker_tar.add("/tmp/"+str(current_user.id)+"-"+project.name+"-Dockerfile", "Dockerfile")
#     if project.requirements != "":
#         required_libs = open("/tmp/"+str(current_user.id)+"-"+project.name+"-requirements.txt", "w")
#         required_libs.write(project.requirements)
#         required_libs.close()
#         docker_tar.add("/tmp/"+str(current_user.id)+"-"+project.name+"-requirements.txt", "requirements.txt")
#     docker_tar.close()
#     try:
# 	    os.remove("/tmp/"+str(current_user.id)+"-"+project.name+"-Dockerfile")
# 	    os.remove("/tmp/"+str(current_user.id)+"-"+project.name+"-requirements.txt")
#     except:
# 		pass

#     comp_buffer = StringIO()
#     with open("/tmp/"+str(current_user.id)+"-"+project.name+"-docker.tar", 'rb') as fh:
#         comp_buffer.write(fh.read())
#     comp_buffer.seek(0)
#     return [comp_buffer, "/tmp/"+str(current_user.id)+"-"+project.name+"-docker.tar"]

def upload_handler(current_user, container, file_obj, kind):
    dest_filename = str(current_user.id)+"-"+str(container.id)+"-%s.tar"%kind #kind is record| signature

    print "About to write..."
    # with open(dest_filename, 'wb') as fh:
    #     # print "Content: %s" %file_obj.read()
    #     # file_obj.seek(0)
    #     fh.write(file_obj.read())

    try:
        s3.Bucket('ddsm-bucket').put_object(Key=str(current_user.id)+"-"+str(container.id)+"-%s.tar"%kind, Body=file_obj.read())
    except:
        print traceback.print_exc()

    if kind in ["docker", "rocket", "kubernetes", "unknown"]:
        container.image['location'] = dest_filename
        container.image['size'] = file_obj.tell()
    # if kind == "binary":
    #     record.image['binary'] = {'type':'executable', 'location':dest_filename, 'size':os.path.getsize(dest_filename)}
    # if kind == "source":
    #     record.image['source'] = {'type':'code', 'location':dest_filename, 'size':os.path.getsize(dest_filename)}
    # if kind == "signature":
    #     record.signature = {'location':dest_filename, 'size':os.path.getsize(dest_filename)}
    print "%s saving..."%kind
    container.save()

# def against_handler(current_user, record, file_obj):
#     ref_name = os.path.join('/tmp/', record.project.name+"-"+str(record.id)+"-against-"+hashlib.sha256(b'Against%s_%s'%(str(record.id), str(datetime.datetime.now))).hexdigest()+".tar")
#     with open(ref_name, 'wb') as fh:
#         fh.write(file_obj.read())

#     ref_tar = tarfile.open(ref_name)
#     base_tar = tarfile.open(record.signature['location'])
#     exploded = {}
#     exploded["reference"] = validate_signature(ref_tar)
#     exploded["base"] = validate_signature(base_tar)
#     print str(exploded)

#     base_signature = load_signature(record)
#     base_signature[0].seek(0)
#     # print "Base: %s"%base_signature[0].read()
#     ref_buffer = StringIO()
#     with open(ref_name, 'rb') as fh:
#         ref_buffer.write(fh.read())
#     ref_buffer.seek(0)
#     # print "Reference: %s"%ref_buffer.read() 
    

#     # d = difflib.Differ()
#     # diff = difflib.unified_diff(base, ref)

#     ratio = difflib.SequenceMatcher(None, base_signature[0].readlines(), ref_buffer.readlines()).ratio()

#     if ratio == 1.0:
#         record.repeated = record.repeated + 1
#         record.save()
#         return json.dumps({'conclusion':'repeated', 'distance': ratio})
#     else:
#         print "More complicated. We need to split the tar file compare the inputs and the outputs and generate the matrix or reproducibility."
#         # record.repeated = record.repeated + 1 if same input, same output
#         # record.reproduced = record.reproduced + 1 if different input, same output

#         # record.repeated = -1 if same input, different output
#         # print '\n'.join(list(diff))
    
#         return json.dumps({'conclusion':'complex', 'distance': ratio})

def load_image(container):
    image_buffer = StringIO()
    with open(container.image['location'], 'rb') as fh:
        image_buffer.write(fh.read())
    image_buffer.seek(0)
    return [image_buffer, container.image['location']]

# def load_signature(record):
#     signature_buffer = StringIO()
#     with open(record.signature['location'], 'rb') as fh:
#         signature_buffer.write(fh.read())
#     signature_buffer.seek(0)
#     return [signature_buffer, record.signature['location']]

# def validate_signature(tar):
#     members = []
#     for member in tar.getmembers():
#         f=tar.extractfile(member)
#         content=f.read()
#         members.append({"name":member.name, "content":content})
#         print "%s has %d newlines" %(member, content.count("\n"))
#         print "%s has %d spaces" % (member,content.count(" "))
#         print "%s has %d characters" % (member, len(content))
#     tar.close()
#     return members


import endpoints
