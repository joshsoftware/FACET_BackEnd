import uuid


def create_slug(data):
    slug = data.lower().replace(" ","-")
    return slug

def create_id():
    return str(uuid.uuid4())