from requests import Request, Session
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
import requests
from app.helpers.utils import is_fit_to_run, store_results,get_current_user
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
    environment = EnvModel.get_one_env(data['environment'])['url']
    if is_fit_to_run(testsuite):
        res = []
        for testcase in testsuite['testcases']:
            testcase['endpoint'] = environment + testcase['endpoint']['endpoint']
            testcase['header'] = testcase['header']['header']
            payload = testcase['payload']['payload']
            expected_outcome = testcase['payload']['expected_outcome']
            testdata = testcase['testdata'] if len(testcase['testdata']) else [{"name": "Payload", "payload":{}, "expected_outcome": {}}]

            testcase_resp = []
            is_testcase_passed = True
            no_of_passed_testcases = 0
            no_of_failed_testcases = 0
            for td in testdata:
                testcase['payload'] = td['payload']
                # TO DO: Expected Outcome to be completed
                # testcase['expected_outcome'] = {**expected_outcome, **td['expected_outcome']}
                testcase['expected_outcome'] = td['expected_outcome']
                testcase['parameters'] = td['parameters']
                resp = perform_testcases(testcase, testsuite, user)
                if resp['status']=='failed':
                    is_testcase_passed = False
                    no_of_failed_testcases += 1
                else:
                    no_of_passed_testcases += 1
                testcase_resp.append({
                    "name": td['name'],
                    **resp
                })
            
            status = "passed" if is_testcase_passed else "failed"
            res.append({
                "testcase_id": testcase['id'],
                "name": testcase['name'],
                "status": status,
                "response": testcase_resp,
                "no_of_passed_testcases": no_of_passed_testcases,
                "no_of_failed_testcases": no_of_failed_testcases
            })
        
        TempModel.get_all_and_delete(testsuite['id'])
        return jsonify({"result": res}), 200
    else:
        return jsonify({"Error" : "Your testcase has missing components"}),400



def fetch_from_api(testcase):
    # r = Request(testcase['method'], testcase['endpoint'], json=testcase['payload'], headers=testcase['header'])

    # prepped = s.prepare_request(r)
    # resp = s.send(prepped)
    # return resp
    if testcase['method'].lower()=='get':
        r = requests.get(url=testcase['endpoint'], json=testcase['payload'], headers=testcase['header'], params=testcase['parameters'])
    elif testcase['method'].lower()=='post':
        r = requests.post(url=testcase['endpoint'], json=testcase['payload'], headers=testcase['header'], params=testcase['parameters'])
    elif testcase['method'].lower()=='put':
        r = requests.put(url=testcase['endpoint'], json=testcase['payload'], headers=testcase['header'], params=testcase['parameters'])
    elif testcase['method'].lower()=='patch':
        r = requests.patch(url=testcase['endpoint'], json=testcase['payload'], headers=testcase['header'], params=testcase['parameters'])
    elif testcase['method'].lower()=='delete':
        r = requests.delete(url=testcase['endpoint'], json=testcase['payload'], headers=testcase['header'], params=testcase['parameters'])
    return r

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
    
    
    status, errors = validate_expected_outcome(testcase, res)

    store_results(
        {
            "testsuite_id": testsuite['id'], 
            "testcase_id": testcase['id'], 
            "response": res.json(),
            "status" : status,
            "payload_used" : testcase['payload'],
            "project_id" : testcase['project_id'],
            "user" : user
        })

    if status == "passed":
        return {"testcase_id":testcase['id'], "status":"passed"}
    else:
        return {"testcase_id":testcase['id'], "status":"failed", "errors":errors, "response": res.text}

def validate_expected_outcome(testcase,response):
    status = 1
    err = []
    res = response.json()
    for field in testcase['expected_outcome']:
        field_name = field.get('name')
        field_type = field.get('type')
        errors = {}

        if field_name == 'status_code':
            status_code = field['value']
        else:
            res_value = res.get(field_name)

            if field['isExact']:
                if field.get('value')==res_value:
                    status
                else:
                    status = 0
                    errors["value"] = f"Outcome value is not matched with Expected value. Expected value is {field.get('value')} but got {res_value}"
            elif field.get('validations'):
                validations = field.get('validations')
                
                max_length = validations.get('maxLength')
                min_length = validations.get('minLength')
                max_value = validations.get('maxValue')
                min_value = validations.get('minValue')
                regex_pattern = validations.get('regex')

                if max_length and len(res_value)>int(max_length):
                    errors['maxLength'] =  f"Outcome value has more length than expected length. Expected length is {max_length} but got {len(res_value)}"
                if min_length and len(res_value)<int(min_length):
                    errors['minLength'] =  f"Outcome value has less length than expected length. Expected length is {min_length} but got {len(res_value)}"
                if min_value and int(res_value)<int(min_value):
                    errors['minValue'] =  f"Outcome value is less than expected length. Expected value is {min_value} but got {res_value}"
                if max_value and int(res_value)>int(max_value):
                    errors['maxValue'] =  f"Outcome value is more than expected length. Expected value is {max_value} but got {res_value}"
                if regex_pattern:
                    pass
        if(len(errors)):
            err.append({"name": field_name, "errors": errors, "res": res})
            
    if int(status_code) == int(response.status_code) and status==1:
        return "passed", err
    return "failed", err
