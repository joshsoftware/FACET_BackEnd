testdata_schema = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "minLength": 3
        },
        "testcase_id": {
            "type": "string",
            "minLength": 1
        },
        "payload": {
            "type": "object"
        },
        "expected_outcome": {
            "type": "object"
        }
    },
    "required": ["name", "testcase_id"]
}