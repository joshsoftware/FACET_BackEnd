testcase_schema = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "minLength": 3
        },
        "endpoint_id": {
            "type": "string",
            "minLength": 1
        },
        "project_id": {
            "type": "string",
            "minLength": 1
        },
        "method": {
            "type": "string",
            "minLength": 3
        },
        "payload_id": {
            "type": "string",
            "minLength": 1
        }
    },
    "required": ["name", "endpoint_id", "project_id", "method", "payload_id"]
}