endpoints_schema = {
    "type":"object",
    "properties": {
        "name": {
            "type":"string",
            "minLength": 4
        },
        "endpoint": {
            "type": "string",
            "minLength": 10
        },
        "project": {
            "type": "string",
            "minLength": 3
        }
    },
    "required": ['name', 'endpoint', 'project']
}