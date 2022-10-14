from datetime import datetime
import requests
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.helpers.utils import is_fit_to_run,get_current_user
from app.models.EnvModel import EnvModel
from app.models.ResultModel import ResultModel
from app.models.TempModel import TempModel
from app.models.TestcaseModel import TestcaseModel
import json

engine_blueprint = Blueprint('engine', __name__)

@engine_blueprint.route('/api/tests', methods=['POST'])
@jwt_required()
def tests():
    try:
        data = request.json
        user = get_current_user().id
        testcase = TestcaseModel.get_one_testcase(data.get('testcase'))
        environment = EnvModel.get_one_env(data['environment'])

        is_fit, missing_components = is_fit_to_run(testcase)
        if is_fit:
            res = []
            teststep_results_to_store = []
            no_of_passed_teststeps = 0
            no_of_failed_teststeps = 0
            unique_run_time_id = str(testcase['name']) + str(datetime.now())
            for teststep in testcase['teststeps']:
                teststep_resp = []
                testdata_results_to_store = []
                is_teststep_passed = True
                no_of_passed_testdata_combinations = 0
                no_of_failed_testdata_combinations = 0
                endpoint = teststep['endpoint']['endpoint']

                teststep['endpoint'] = environment['url'] + endpoint
                teststep['header'] = teststep['header']['header']
                # testdata = teststep['testdata']
                testdata = [test_data for test_data in teststep['testdata'] if test_data in testcase['testdatas']]
                for td in testdata:
                    td['name'] = "[" + td['name'] + "]"
                    teststep['payload'] = td['payload']
                    teststep['expected_outcome'] = td['expected_outcome']
                    teststep['parameters'] = td['parameters']
                    teststep['name'] = teststep['name'] + td['name']
                    resp = perform_teststeps(teststep, testcase, user, environment,unique_run_time_id)
                    ind = teststep['name'].find(td['name'])
                    teststep['name'] = teststep['name'][:ind]

                    td['name'] = td['name'].strip("[]")
                    if resp['status']=='failed':
                        is_teststep_passed = False
                        no_of_failed_testdata_combinations += 1
                    else:
                        no_of_passed_testdata_combinations += 1
                        
                    teststep_resp.append({
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
                
                if is_teststep_passed:
                    status = "passed"
                    no_of_passed_teststeps += 1
                else:
                    status = "failed"
                    no_of_failed_teststeps += 1
                res.append({
                    "teststep_id": teststep['id'],
                    "name": teststep['name'],
                    "status": status,
                    "response": teststep_resp,
                    "no_of_passed_testdata_combinations": no_of_passed_testdata_combinations,
                    "no_of_failed_testdata_combinations": no_of_failed_testdata_combinations
                })

                teststep_results_to_store.append({
                    "name": teststep.get('name'),
                    "method": teststep.get('method'),
                    "endpoint": endpoint,
                    "header": teststep.get('header'),
                    "payload": teststep.get('payload'),
                    "testdata_combinations": testdata_results_to_store,
                    "status": status,
                    "no_of_passed_testdata_combinations": no_of_passed_testdata_combinations,
                    "no_of_failed_testdata_combinations": no_of_failed_testdata_combinations,
                })
            
            # store teststuite result into the result model
            project = testcase.get('project')
            del testcase['project']
            del testcase['teststeps']
            del testcase['execution_sequence']
            del environment['project']
            data_to_store = {
                "project": project,
                "testcase": testcase,
                "teststeps": teststep_results_to_store,
                "environment": environment,
                "status": status,
                "no_of_passed_teststeps": no_of_passed_teststeps,
                "no_of_failed_teststeps": no_of_failed_teststeps,
                "executed_by": user
            }
            ResultModel(data_to_store).save()
            TempModel.get_all_and_delete(testcase=testcase['id'],run_time_id=unique_run_time_id)
            print(res)
            return jsonify({"result": res}), 200
        else:
            return jsonify({"error" : missing_components}),400
    except Exception as e:
        return jsonify({"Error": str(e)}), 400


def fetch_from_api(teststep):
    # r = Request(teststep['method'], teststep['endpoint'], json=teststep['payload'], headers=teststep['header'])

    # prepped = s.prepare_request(r)
    # resp = s.send(prepped)
    # return resp
    try:
        if teststep['method'].lower()=='get':
            r = requests.get(url=teststep['endpoint'], json=teststep['payload'], headers=teststep['header'], params=teststep['parameters'])
        elif teststep['method'].lower()=='post':
            r = requests.post(url=teststep['endpoint'], json=teststep['payload'], headers=teststep['header'], params=teststep['parameters'])
        elif teststep['method'].lower()=='put':
            r = requests.put(url=teststep['endpoint'], json=teststep['payload'], headers=teststep['header'], params=teststep['parameters'])
        elif teststep['method'].lower()=='patch':
            r = requests.patch(url=teststep['endpoint'], json=teststep['payload'], headers=teststep['header'], params=teststep['parameters'])
        elif teststep['method'].lower()=='delete':
            r = requests.delete(url=teststep['endpoint'], json=teststep['payload'], headers=teststep['header'], params=teststep['parameters'])
        return r
    except Exception as err:
        return str(err)

def perform_teststeps(teststep, testcase, user, environment,unique_run_time_id):
    
    if "$var=" in str(teststep):
        pattern =  "\$var\=(.*?)\'"
        import re
        variable = re.search(pattern, str(teststep)).group(1)
        tmp = variable.split('.')
        var_value = TempModel.get_one(testcase=testcase['id'], teststeps=tmp[0],run_time_id=unique_run_time_id)
        
        if var_value is None:
            outcome  = [
                {
                    "res_value": "Not found",
                    "executed_status": "failed",
                    "status": "failed",
                    "error": "Incorrect Testdata, Testdata does not exist, hence execution failed"
                }
            ]
            return {
                "status" : "failed",
                "outcome" : outcome,
                "response" : {"Error" : "Testdata does not exist hence execution aborted"},
                "no_of_passed_fields": 0,
                "no_of_failed_fields": 0
            }

        for i in tmp[1:len(tmp)]:
            var_value = var_value.get(i)
            
        teststep = eval(str(teststep).replace(f"$var={variable}", var_value))
            
    res = fetch_from_api(teststep)
    if type(res) is str:
        outcome  = [
                {
                    "res_value": "Not found",
                    "executed_status": "failed",
                    "status": "failed",
                    "error": res
                }
            ]
        return {
                "status" : "failed",
                "outcome" : outcome,
                "response" : {"Error" : "Testdata does not exist hence execution aborted"},
                "no_of_passed_fields": 0,
                "no_of_failed_fields": 0
            }
    temp = TempModel({"testcase": testcase['id'], "teststep": teststep['name'], "resp": res.json(), "run_time_id" : unique_run_time_id})
    temp.save()
    
    status, outcome, no_of_passed_fields, no_of_failed_fields = validate_expected_outcome(teststep, res)

    return {
        "status": "passed" if status=="passed" else "failed",
        "outcome": outcome,
        "response": res.json(),
        "no_of_passed_fields": no_of_passed_fields,
        "no_of_failed_fields": no_of_failed_fields
    }

def validate_expected_outcome(teststep, response):
    """
    
    """

    no_of_passed_fields = 0
    no_of_failed_fields = 0
    outcome = []
    res = response.json()
    for field in teststep['expected_outcome']:
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