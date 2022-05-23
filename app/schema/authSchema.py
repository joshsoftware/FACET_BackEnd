signup_schema = {
    "type": "object",
    "properties": {
        "email": {
            "type": "string",
            "format": "([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
        },
        "password": {
            "type":"string",
            "minLength": 4
        },
        "name": {
            "type": "string",
            "minLength": 4
        }
    },
    "required": ['email', 'password', 'name'],
}

login_schema = {
    "type": "object",
    "properties": {
        "email": {
            "type": "string",
            "pattern": "([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
        },
        "password": {
            "type":"string",
            "minLength": 4
        }
    },
    "required": ['email', 'password'],
}