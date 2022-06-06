import re
import uuid
from flask import jsonify
from marshmallow import ValidationError
from slugify import slugify
from flask_jwt_extended import get_current_user

from app.models.ProjectModel import ProjectModel
from app.models.ResultModel import ResultModel, ResultSchema

result_schema = ResultSchema()

def create_slug(data):
    slug = slugify(data, lowercase=True, separator='-')
    return slug

def create_id():
    return str(uuid.uuid4())


def get_project_id(slug):
    return ProjectModel.query.filter_by(name=slug).first().id


def store_results(data):
    try:
        results = result_schema.load(data)
    except ValidationError as err:
        return jsonify(str(err)), 400
    
    result = ResultModel(results)
    result.save()