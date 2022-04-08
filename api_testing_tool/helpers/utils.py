import uuid
from slugify import slugify


def create_slug(data):
    slug = slugify(data, lowercase=False, separator='-')
    return slug

def create_id():
    return str(uuid.uuid4())