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
        "project_name": {
            "type": "string",
            "minLength": 3
        },
        "header": {
            "type": "string",
            "minLength": 1
        }
    },
    "required": ['name', 'endpoint', 'project_name', 'header']
}