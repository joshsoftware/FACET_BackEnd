import uuid
from flask import jsonify
from slugify import slugify
from flask_jwt_extended import get_current_user
from marshmallow import ValidationError
from app.models.ResultModel import ResultModel,ResultSchema
from app.models.project_model import ProjectModel
from app.models.user_model import UserModel

result_schema = ResultSchema()

def create_slug(data):
    slug = slugify(data, lowercase=True, separator='-')
    return slug

def create_id():
    return str(uuid.uuid4())


def get_project_id(slug):
    project = ProjectModel.query.filter_by(name=slug).first() or None
    if project:
        return project.id
    return None

def store_results(data):
    try:
        results = result_schema.load(data)
    except ValidationError as err:
        return jsonify(str(err)), 400
    
    result = ResultModel(results)
    result.save()

def has_access_to_project(project_id,user_id):
    if project_id is None or user_id is None:
        return False
    return ProjectModel.is_a_member_of_project(project_id,user_id)

def has_access_to_organization(organization_id, user):
    """
    Util function to check if the user currently belongs to the organization or not
    """
    return user.organizations == organization_id

def is_super_admin(user):
    return UserModel.is_super_user(user)

def is_user_admin(user):
    return UserModel.is_user_admin(user)


def get_user_name(id):
    return UserModel.get_user_name(id)

def get_project_members_id(project):
    project = get_project_id(project)
    members = ProjectModel.get_project_members(project)

    members_id = [i['id'] for i in members]
    return members_id

def is_fit_to_run(testcase):
    is_fit = True
    missing_components = {}
    teststeps = testcase['teststeps']
    for teststep in teststeps:
        missing_components[teststep['name']] = []
        testdata = [test_data for test_data in teststep['testdata'] if test_data in testcase['testdatas']]
        if teststep['endpoint'] == None:
            missing_components[teststep['name']].append('endpoint missing')
            is_fit = False
        if teststep['header'] == None:
            missing_components[teststep['name']].append('header missing')
            is_fit = False
        if teststep['payload'] == None:
            missing_components[teststep['name']].append('payload missing')
            is_fit = False
        if testdata is None or len(testdata) == 0:
            missing_components[teststep['name']].append('testdata missing')
            is_fit = False
        if len(missing_components[teststep['name']]) == 0:
            del missing_components[teststep['name']]
    return is_fit,missing_components