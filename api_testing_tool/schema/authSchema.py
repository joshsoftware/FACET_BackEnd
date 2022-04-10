signup_schema = {
    "type": "object",
    "properties": {
        "email": {
            "type": "string",
            "minLength": 6
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
            "minLength": 6
        },
        "password": {
            "type":"string",
            "minLength": 4
        }
    },
    "required": ['email', 'password'],
}