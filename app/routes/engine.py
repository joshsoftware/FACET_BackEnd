from datetime import datetime
import requests
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.helpers.utils import is_fit_to_run, get_current_user
from app.models.EnvModel import EnvModel
from app.models.ResultModel import ResultModel
from app.models.TempModel import TempModel
from app.models.TestcaseModel import TestcaseModel
from app.models.TestsuiteModel import TestsuiteModel
import logging

engine_blueprint = Blueprint('engine', __name__)


@engine_blueprint.route('/api/tests', methods=['POST'])
@jwt_required()
def engine():
    """
    POST Request API for executing testsuite or testcases
    Requires:
        - method: POST
        - JWT Bearer token in Authorization header
        - body data:
            {
                "testsuite" : testsuite_id (integer) [Optional, only if level is testsuite]
                "environment" : environment_id (integer)
                "level" : string -> either "testsuite" or "testcase"
                "testcase" : testcase_id (integer) [Optional, only if level is testcase]
            }
        - Note either testcase or testsuite field is required to be sent, and that field should match the string
          in level field.
    Response:
        - If success, then json response with status code 200, where json look like :
            {
                "result" :{
                    "name" : name of testsuite or testcase depending upon execution level,
                    "no_of_passed_fields" : integer,
                    "no_of_failed_fields" : integer,
                    "status" : "passed" or "failed"
                },
                "result_id" : integer
            }
        - Error message "something went wrong" with status code 400 if anything goes wrong due to data inconsistency or server issue.
        - Error message "testcase_name : [missing_component_field] with status code 400 if any component is missing during testcase execution
    """
    try:
        req_data = request.json
        user = get_current_user().id
        logging.info(f"POST request to execute by user:{user} with payload:{req_data}")
        is_req_data_valid = ((req_data.get('testsuite') and req_data.get('level') == 'testsuite') or (req_data.get('testcase') and req_data.get('level') == 'testcase')) and req_data.get('environment')

        if not is_req_data_valid:
            logging.info(f"POST request to execute failed due to faulty input")
            return jsonify({"error": "incomplete request, kindly send all required parameters"}), 400

        execution_data = {'user': user}
        environment = EnvModel.get_one_env(req_data['environment'])
        if req_data.get('level') == "testsuite":
            testsuite = TestsuiteModel.get_one_testsuite(id=req_data['testsuite'])
            logging.debug(f"testsuite execute begins with testsuite={testsuite['id']} with environment:{environment['id']}")
            no_of_passed_testcases = 0
            no_of_failed_testcases = 0
            testcase_result_to_store = []
            data_to_send = []
            status = "passed"
            testcase_status = "passed"
            for testcase in testsuite['testcases']:
                execution_data['environment'] = environment
                execution_data['testcase'] = testcase
                resp = tests(data=execution_data)

                del testcase['project']
                del testcase['teststeps']
                del testcase['execution_sequence']
                del testcase['testdatas']

                #Error handling condition for testcase, in case the testcase has missing components or the function blows up due to any other error
                if resp.get('error'):
                    no_of_failed_testcases += 1
                    testcase_result_to_store.append({
                        "status": "aborted",
                        "no_of_passed_teststeps": 0,
                        "no_of_failed_teststeps": 0,
                        "testcase" : testcase,
                        "teststeps" : {
                            "error": resp['error']
                        }
                    })
                    data_to_send.append({
                        "status" : "failed",
                        "no_of_passed_fields": 0,
                        "no_of_failed_fields": 0,
                        "name" : testcase['name'],
                        "testcase_id" : testcase['id']
                    })
                else:
                    if resp['result']['status'] == "failed":
                        no_of_failed_testcases += 1
                        status = "failed"
                        testcase_status = "failed"
                    else:
                        no_of_passed_testcases += 1
                        testcase_status = "passed"
                    
                    testcase_result_to_store.append({
                        "status" : testcase_status,
                        "no_of_passed_teststeps": resp['result']['no_of_passed_teststeps'],
                        "no_of_failed_teststeps": resp['result']['no_of_failed_teststeps'],
                        "testcase" : testcase,
                        "teststeps": resp['result']['teststeps']
                    })
                    data_to_send.append({
                    "status" : testcase_status,
                    "no_of_passed_fields": resp['result']['no_of_passed_teststeps'],
                    "no_of_failed_fields": resp['result']['no_of_failed_teststeps'],
                    "name" : testcase['name'],
                    "testcase_id" : testcase['id']
                })

            project = testsuite['project']
            del testsuite['project']
            del testsuite['testcases']

            testsuite_execution_result = {
                "no_of_passed_testcases" : no_of_passed_testcases,
                "no_of_failed_testcases" : no_of_failed_testcases,
                "testsuite" : testsuite,
                "testsuite_execution" : testcase_result_to_store
            }

            data_to_store = {
                "project" : project,
                "environment" : environment,
                "level" : "testsuite",
                "result" : testsuite_execution_result,
                "executed_by": user,
                "status" : status
            }
            result = ResultModel(data_to_store)
            result.save()
            logging.info(f"testsuite execution successful")
            if no_of_failed_testcases > 0:
                status = "failed"

            return jsonify({"result": data_to_send, "result_id": result.id}), 200
        #Execution of a single testcase
        elif req_data.get('level') == "testcase":
            execution_data['environment'] = environment
            execution_data['testcase'] = TestcaseModel.get_one_testcase(req_data['testcase'])
            response = tests(data=execution_data)

            if response.get('error'):
                logging.info(f"POST request for testcase execution failed due to the following error:{response['error']}")
                return jsonify({"error": response['error']}), 400
            else:
                result_to_store = {
                    "project" : execution_data['testcase']['project'],
                    "environment" : execution_data['environment'],
                    "status" : response['result']['status'],
                    "level" : "testcase",
                    "executed_by" : user 
                }
                del response['result']['status']
                result_to_store['result'] = response['result']
                result_to_store['result']['testcase'] = execution_data['testcase']
                del result_to_store['result']['testcase']['project']
                del result_to_store['result']['testcase']['teststeps']
                del result_to_store['result']['testcase']['execution_sequence']
                del result_to_store['result']['testcase']['testdatas']
                
                result = ResultModel(result_to_store)
                result.save()
                logging.info(f"testcase execution successful")
                return jsonify({"result": response['result_to_show'], "result_id": result.id}), 200
        else:
            logging.info(f"POST request for execution failed due to faulty payload")
            return jsonify({"error" : "faulty request, kindly check the data you're sending"}), 400
    except Exception as err:
        logging.info(f"POST request for execution failed due to the following error:{err}")
        return jsonify({"error": "something went wrong"}), 400

def tests(data):
    try:
        testcase = data['testcase']
        environment = data['environment']
        user = data['user']
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
                
                testdata = [test_data for test_data in teststep['testdata'] if test_data in testcase['testdatas']]
                for td in testdata:
                    td['name'] = "[" + td['name'] + "]"
                    teststep['payload'] = td['payload']
                    teststep['expected_outcome'] = td['expected_outcome']
                    teststep['parameters'] = td['parameters']
                    teststep['name'] = teststep['name'] + td['name']
                    resp = perform_teststeps(teststep, testcase, user, environment, unique_run_time_id)
                    
                    ind = teststep['name'].find(td['name'])
                    teststep['name'] = teststep['name'][:ind]

                    td['name'] = td['name'].strip("[]")
                    if resp['status'] == 'failed':
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
                    "no_of_passed_fields": no_of_passed_testdata_combinations,
                    "no_of_failed_fields": no_of_failed_testdata_combinations
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
            data_to_store = {
                "teststeps": teststep_results_to_store,
                "status": status,
                "no_of_passed_teststeps": no_of_passed_teststeps,
                "no_of_failed_teststeps": no_of_failed_teststeps,
            }
            TempModel.get_all_and_delete(testcase=testcase['id'], run_time_id=unique_run_time_id)
            return {"result": data_to_store, "result_to_show": res}
        else:
            return {"error": missing_components}
    except Exception as err:
        return {"error": str(err)}


def fetch_from_api(teststep):
    try:
        if teststep['method'].lower() == 'get':
            r = requests.get(url=teststep['endpoint'], json=teststep['payload'],
                             headers=teststep['header'], params=teststep['parameters'])
        elif teststep['method'].lower() == 'post':
            r = requests.post(url=teststep['endpoint'], json=teststep['payload'],
                              headers=teststep['header'], params=teststep['parameters'])
        elif teststep['method'].lower() == 'put':
            r = requests.put(url=teststep['endpoint'], json=teststep['payload'],
                             headers=teststep['header'], params=teststep['parameters'])
        elif teststep['method'].lower() == 'patch':
            r = requests.patch(url=teststep['endpoint'], json=teststep['payload'],
                               headers=teststep['header'], params=teststep['parameters'])
        elif teststep['method'].lower() == 'delete':
            r = requests.delete(url=teststep['endpoint'], json=teststep['payload'],
                                headers=teststep['header'], params=teststep['parameters'])
        return r
    except Exception as err:
        return str(err)


def perform_teststeps(teststep, testcase, user, environment, unique_run_time_id):

    if "$var=" in str(teststep):
        pattern = "\$var\=(.*?)\'"
        import re
        variable = re.search(pattern, str(teststep)).group(1)
        tmp = variable.split('.')
        var_value = TempModel.get_one(
            testcase=testcase['id'], teststeps=tmp[0], run_time_id=unique_run_time_id)

        if var_value is None:
            outcome = [
                {
                    "res_value": "Not found",
                    "executed_status": "failed",
                    "status": "failed",
                    "error": "Incorrect Testdata, Testdata does not exist, hence execution failed",
                    "is_status_manually_updated" : False
                }
            ]
            return {
                "status": "failed",
                "outcome": outcome,
                "response": {"Error": "Testdata does not exist hence execution aborted"},
                "no_of_passed_fields": 0,
                "no_of_failed_fields": 0
            }

        for i in tmp[1:len(tmp)]:
            var_value = var_value.get(i)
        teststep = eval(str(teststep).replace(f"$var={variable}", var_value))

    res = fetch_from_api(teststep)
    if type(res) is str:
        outcome = []
        for field in teststep['expected_outcome']:
            outcome.append({
                    **field,
                    "res_value": "Not found",
                    "executed_status": "failed",
                    "status": "failed",
                    "error": res,
                    "is_status_manually_updated" : False
                })
        return {
            "status": "failed",
            "outcome": outcome,
            "response": {"error": res},
            "no_of_passed_fields": 0,
            "no_of_failed_fields": 0
        }
    temp = TempModel({"testcase": testcase['id'], "teststep": teststep['name'], "resp": res.json(
    ), "run_time_id": unique_run_time_id})
    temp.save()

    status, outcome, no_of_passed_fields, no_of_failed_fields = validate_expected_outcome(
        teststep, res)

    return {
        "status": "passed" if status == "passed" else "failed",
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
                is_failed = True
                error = f"Expected Field not found in response."
            else:
                if field['isExact']:
                    if field.get('value') != res_value:
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
                    if max_length and len(res_value) > int(max_length):
                        err.append('maxLength')
                    if min_length and len(res_value) < int(min_length):
                        err.append('minLength')
                    if min_value and int(res_value) < int(min_value):
                        err.append('minValue')
                    if max_value and int(res_value) > int(max_value):
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
            "is_status_manually_updated" : False
        })

        if is_failed:
            no_of_failed_fields += 1
        else:
            no_of_passed_fields += 1

    if no_of_failed_fields == 0:
        return "passed", outcome, no_of_passed_fields, no_of_failed_fields
    return "failed", outcome, no_of_passed_fields, no_of_failed_fields
