from requests import Request, Session
from flask import Blueprint, request, jsonify
from api_testing_tool import db
from api_testing_tool.helpers.utils import create_id, get_project_id
from flask_jwt_extended import get_current_user, jwt_required

engine_blueprint = Blueprint('engine', __name__)

s = Session()

@engine_blueprint.route('/api/tests', methods=['POST'])
@jwt_required()
def tests():
    data = request.json
    project_id = get_project_id(data.get("project"))
    testsuite = db.testsuite.find_one({"name":data.get("testsuite"),"project" : project_id})
    testsuite['environment'] = db.envtypes.find_one({"_id": testsuite['environment']}, {"project": 0, "user": 0})
    res = []

    for i in testsuite['testcases']:
        testcase = db.testcases.find_one({"_id":i})
        endpoint = db.endpoints.find_one({"_id": testcase['endpoint']})
        header = db.headers.find_one({"_id": testcase['header']})
        payload = db.payloads.find_one({"_id":testcase['payload']})
        testdata = testcase['testdata'] if len(testcase['testdata']) else [{"name": "Payload", "payload":{}, "expected_outcome": {}}]

        testcase['endpoint'] = testsuite['environment']['url'] + endpoint['endpoint']
        testcase['header'] = header['header']
        testcase_resp = []
        for j in testdata:
            testcase['payload'] = {**payload['payload'], **j['payload']}
            testcase['expected_outcome'] = {**payload['expected_outcome'], **j['expected_outcome']}
            resp = perform_testcases(testcase, testsuite)
            testcase_resp.append({
                "testdata_name": j['name'],
                **resp
            })
        
        res.append({
            "testcase_id": testcase['_id'],
            "name": testcase['name'],
            "response": testcase_resp
        })
    # db.temp.delete_many({"testsuite":testsuite['_id']})
    return jsonify(res)

def fetch_from_api(testcase):
    r = Request(testcase['method'], testcase['endpoint'], json=testcase['payload'], headers=testcase['header'])
    prepped = s.prepare_request(r)
    resp = s.send(prepped)
    return resp

def perform_testcases(testcase, testsuite):
    if "$var=" in str(testcase):
        pattern =  "\$var\=(.*?)\'"
        import re
        variable = re.search(pattern, str(testcase)).group(1)
        tmp = variable.split('.')
        var_value = db.temp.find_one({"testsuite": testsuite['_id'], "testcase":tmp[0]})
        for i in tmp[1:len(tmp)]:
            var_value = var_value.get(i)
        testcase = eval(str(testcase).replace(f"$var={variable}", var_value))
    res = fetch_from_api(testcase)

    # Add response to temp collection
    db.temp.insert_one({
        "_id": create_id(),
        "testsuite": testsuite['_id'],
        "testcase" : testcase['name'],
        "resp": res.json()
    })

    if res.status_code==testcase['expected_outcome']['status_code']:
        return {"status":"passed"}
    else:
        return {"status":"failed", "response":res.json()}
