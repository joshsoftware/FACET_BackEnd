environments_schema = {
    "type":"object",
    "properties": {
        "name": {
            "type":"string",
            "minLength": 4
        },
        "url": {
            "type": "string",
            "minLength": 10
        },
        "project": {
            "type": "string",
            "minLength": 3
        }
    },
    "required": ['name', 'url', 'project']
}