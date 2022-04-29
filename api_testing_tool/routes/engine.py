from requests import Request, Session
from flask import Blueprint, request, jsonify
from api_testing_tool import db
from api_testing_tool.helpers.utils import create_id

engine_blueprint = Blueprint('engine', __name__)

s = Session()

@engine_blueprint.route('/api/tests', methods=['POST'])
def tests():
    data = request.json

    testsuite = db.testsuite.find_one({"_id":data.get("testsuite")})
    res = []

    for i in testsuite['testcases']:
        testcase = db.testcases.find_one({"_id":i})

        endpoint = db.endpoints.find_one({"_id": testcase['endpoint']})
        header = db.headers.find_one({"_id": testcase['header']})
        payload = db.payloads.find_one({"_id":testcase['payload']})
        testdata = testcase['testdata'][0] if len(testcase['testdata']) else {"payload":{}, "expected_outcome": {}}

        testcase['endpoint'] = endpoint['endpoint']
        testcase['header'] = header['header']
        testcase['payload'] = {**payload['payload'], **testdata['payload']}
        testcase['expected_outcome'] = {**payload['expected_outcome'], **testdata['expected_outcome']}

        res.append(perform_testcases(testcase, testsuite))
        
    db.temp.delete_many({"testsuite":testsuite['_id']})
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
        return {"testcase_id":testcase['_id'], "name":testcase['name'], "status":"passed"}
    else:
        return {"testcase_id":testcase['_id'], "name":testcase['name'], "status":"failed", "response":res.json()}
