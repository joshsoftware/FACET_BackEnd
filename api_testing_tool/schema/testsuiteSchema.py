testsuite_schema = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "minLength": 3
        },
        "description": {
            "type": "string"
        },
        "project": {
            "type": "string",
            "minlength": 1
        },
        "testcases": {
            "type": "array",
            "items": {
                "type": "string",
                "minLength": 1
            }
        },
        "environment": {
            "type": "string",
            "minLength": 1
        }
    },
    "required": ["name", "project", "testcases", "environment"]
}