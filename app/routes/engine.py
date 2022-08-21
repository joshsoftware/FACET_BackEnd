import requests
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.helpers.utils import is_fit_to_run,get_current_user
from app.models.EnvModel import EnvModel
from app.models.ResultModel import ResultModel
from app.models.TempModel import TempModel
from app.models.TestsuiteModel import TestsuiteModel

engine_blueprint = Blueprint('engine', __name__)

# s = Session()

@engine_blueprint.route('/api/tests', methods=['POST'])
@jwt_required()
def tests():
    try:
        data = request.json
        user = get_current_user().id
        testsuite = TestsuiteModel.get_one_testsuite(data.get('testsuite'))
        environment = EnvModel.get_one_env(data['environment'])

        if is_fit_to_run(testsuite):
            res = []
            testcase_results_to_store = []
            no_of_passed_testcases = 0
            no_of_failed_testcases = 0
            for testcase in testsuite['testcases']:
                testcase_resp = []
                testdata_results_to_store = []
                is_testcase_passed = True
                no_of_passed_testdata_combinations = 0
                no_of_failed_testdata_combinations = 0
                endpoint = testcase['endpoint']['endpoint']

                testcase['endpoint'] = environment['url'] + endpoint
                testcase['header'] = testcase['header']['header']
                testdata = testcase['testdata'] if len(testcase['testdata']) else [{"name": "Payload","parameters": {}, "payload":{}, "expected_outcome": {}}]

                for td in testdata:
                    testcase['payload'] = td['payload']
                    testcase['expected_outcome'] = td['expected_outcome']
                    testcase['parameters'] = td['parameters']
                    resp = perform_testcases(testcase, testsuite, user, environment)
                    if resp['status']=='failed':
                        is_testcase_passed = False
                        no_of_failed_testdata_combinations += 1
                    else:
                        no_of_passed_testdata_combinations += 1
                        
                    testcase_resp.append({
                        "name": td['name'],
                        **resp
                    })

                    testdata_results_to_store.append({
                        "testdata": td,
                        "name": td['name'],
                        "parameters": td['parameters'],
                        "payload": td['payload'],
                        **resp
                    })
                
                if is_testcase_passed:
                    status = "passed"
                    no_of_passed_testcases += 1
                else:
                    status = "failed"
                    no_of_failed_testcases += 1
                    
                res.append({
                    "testcase_id": testcase['id'],
                    "name": testcase['name'],
                    "status": status,
                    "response": testcase_resp,
                    "no_of_passed_testdata_combinations": no_of_passed_testdata_combinations,
                    "no_of_failed_testdata_combinations": no_of_failed_testdata_combinations
                })

                testcase_results_to_store.append({
                    "name": testcase.get('name'),
                    "method": testcase.get('method'),
                    "endpoint": endpoint,
                    "header": testcase.get('header'),
                    "payload": testcase.get('payload'),
                    "testdata_combinations": testdata_results_to_store,
                    "status": status,
                    "no_of_passed_testdata_combinations": no_of_passed_testdata_combinations,
                    "no_of_failed_testdata_combinations": no_of_failed_testdata_combinations,
                })
            
            # store teststuite result into the result model
            project = testsuite.get('project')
            del testsuite['project']
            del testsuite['testcases']
            del testsuite['execution_sequence']
            del environment['project']
            data_to_store = {
                "project": project,
                "testsuite": testsuite,
                "testcases": testcase_results_to_store,
                "environment": environment,
                "status": status,
                "no_of_passed_testcases": no_of_passed_testcases,
                "no_of_failed_testcases": no_of_failed_testcases,
                "executed_by": user
            }
            ResultModel(data_to_store).save()

            TempModel.get_all_and_delete(testsuite['id'])
            return jsonify({"result": res}), 200
        else:
            return jsonify({"error" : "Your testcase has missing components"}),400
    except Exception as e:
        return jsonify({"error": str(e)}), 400


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

def perform_testcases(testcase, testsuite, user, environment):
    
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
    
    
    status, outcome, no_of_passed_fields, no_of_failed_fields = validate_expected_outcome(testcase, res)

    return {
        "status": "passed" if status=="passed" else "failed",
        "outcome": outcome,
        "response": res.json(),
        "no_of_passed_fields": no_of_passed_fields,
        "no_of_failed_fields": no_of_failed_fields
    }

def validate_expected_outcome(testcase, response):
    """
    
    """

    no_of_passed_fields = 0
    no_of_failed_fields = 0
    outcome = []
    res = response.json()
    for field in testcase['expected_outcome']:
        field_name = field.get('name')
        # field_type = field.get('type')
        res_value = ""
        error = ""
        is_failed = False

        if field_name == 'status_code':
            res_value = response.status_code
            if int(field['value']) != int(res_value):
                is_failed = True
                error = f"Status code of response is not matched with Expected status code."
        else:
            res_value = res.get(field_name)
            if not res_value:
                is_failed =  True
                error = f"Expected Field not found in response."
            else:
                if field['isExact']:
                    if field.get('value')!=res_value:
                        is_failed = True
                        error = f"Response value is not matched with Expected value."
                elif field.get('validations'):
                    validations = field.get('validations')
                    
                    max_length = validations.get('maxLength')
                    min_length = validations.get('minLength')
                    max_value = validations.get('maxValue')
                    min_value = validations.get('minValue')
                    regex_pattern = validations.get('regex')

                    err = []
                    if max_length and len(res_value)>int(max_length):
                        err.append('maxLength')
                    if min_length and len(res_value)<int(min_length):
                        err.append('minLength')
                    if min_value and int(res_value)<int(min_value):
                        err.append('minValue')
                    if max_value and int(res_value)>int(max_value):
                        err.append('maxValue')
                    if regex_pattern:
                        pass

                    if len(err):
                        is_failed = True
                        error = f"Validations not matched: {err}"
        
        outcome.append({
            **field, 
            "res_value": res_value,
            "executed_status": "failed" if is_failed else "passed",
            "status": "failed" if is_failed else "passed",
            "error": error,
        })

        if is_failed:
            no_of_failed_fields += 1
        else:
            no_of_passed_fields += 1
    
    if no_of_failed_fields==0:
        return "passed", outcome, no_of_passed_fields, no_of_failed_fields
    return "failed", outcome, no_of_passed_fields, no_of_failed_fields
