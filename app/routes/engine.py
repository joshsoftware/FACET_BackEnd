from requests import Request, Session
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.helpers.utils import store_results,get_current_user
from app.models.EnvModel import EnvModel
from app.models.TempModel import TempModel
from app.models.TestsuiteModel import TestsuiteModel

engine_blueprint = Blueprint('engine', __name__)

s = Session()

@engine_blueprint.route('/api/tests', methods=['POST'])
@jwt_required()
def tests():
    data = request.json
    user = get_current_user().id
    testsuite = TestsuiteModel.get_one_testsuite(data.get('testsuite'))
    environment = EnvModel.get_one_env(testsuite['environment'])['url']

    res = []
    for testcase in testsuite['testcases']:
        testcase['endpoint'] = environment + testcase['endpoint']['endpoint']
        testcase['header'] = testcase['header']['header']
        payload = testcase['payload']['payload']
        expected_outcome = testcase['payload']['expected_outcome']
        testdata = testcase['testdata'] if len(testcase['testdata']) else [{"name": "Payload", "payload":{}, "expected_outcome": {}}]

        testcase_resp = []
        for td in testdata:
            testcase['payload'] = {**payload, **td['payload']}
            testcase['expected_outcome'] = {**expected_outcome, **td['expected_outcome']}
            resp = perform_testcases(testcase, testsuite,user)
            testcase_resp.append({
                "name": td['name'],
                **resp
            })
        
        res.append({
            "testcase_id": testcase['id'],
            "name": testcase['name'],
            "response": testcase_resp
        })
    
    TempModel.get_all_and_delete(testsuite['id'])
    return jsonify(res)



def fetch_from_api(testcase):
    r = Request(testcase['method'], testcase['endpoint'], json=testcase['payload'], headers=testcase['header'])

    prepped = s.prepare_request(r)
    resp = s.send(prepped)

    return resp

def perform_testcases(testcase, testsuite,user):
    
    if "$var=" in str(testcase):
        pattern =  "\$var\=(.*?)\'"
        import re
        variable = re.search(pattern, str(testcase)).group(1)
        tmp = variable.split('.')

        var_value = TempModel.get_one(testsuite=testsuite['id'], testcase=tmp[0])
        
        for i in tmp[1:len(tmp)]:
            var_value = var_value.get(i)
            
        testcase = eval(str(testcase).replace(f"$var={variable}", var_value))
            
    res = fetch_from_api(testcase)

    temp = TempModel({"testsuite": testsuite['id'], "testcase": testcase['name'], "resp": res.json()})
    temp.save()
    store_results(
        {
            "testsuite_id": testsuite['id'], 
            "testcase_id": testcase['id'], 
            "response": res.json(), 
            "payload_used" : testcase['payload'],
            "project_id" : testcase['project_id'],
            "user" : user
        })
    if res.status_code==testcase['expected_outcome']['status_code']:
        return {"testcase_id":testcase['id'], "name":testcase['name'], "status":"passed"}
    else:
        return {"testcase_id":testcase['id'], "name":testcase['name'], "status":"failed", "response":res.json()}
