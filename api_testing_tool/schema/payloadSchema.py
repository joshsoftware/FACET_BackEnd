payload_schema = {
    "type": "object",
    "properties": {
        "name": {
            "type":"string",
            "minLength": 3
        },
        "project": {
            "type": "string",
            "minLength": 1
        },
        "payload": {
            "type": "object"
        },
        "expected_outcome": {
            "type": "object",
            "properties": {
                "status_code": {
                    "type": "integer",
                    "minLength": 1
                }
            },
            "required": ["status_code"]
        }
    },
    "required": ["name", "project", "payload", "expected_outcome"]
}