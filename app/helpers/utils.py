import re
import uuid
from slugify import slugify
from flask_jwt_extended import get_current_user

from app.models.ProjectModel import ProjectModel


def create_slug(data):
    slug = slugify(data, lowercase=False, separator='-')
    return slug

def create_id():
    return str(uuid.uuid4())

def validation_error(e, ind=0):
    
    if len(e.relative_path) > ind:
        error = {e.relative_path[ind] : validation_error(e, ind=ind+1)}
    elif len(e.relative_path) > 0:
        print(str(e.message))
        error = re.sub("'()*'", e.relative_path[ind-1], str(e.message))
    else:
        error = e.message
        
    return error

def get_project_id(slug):
    return ProjectModel.query.filter_by(name=slug).first().id