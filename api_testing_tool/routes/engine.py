from requests import Request, Session
from flask import Blueprint, request, jsonify
from api_testing_tool import db
from api_testing_tool.helpers.utils import create_id

engine_blueprint = Blueprint('engine', __name__)

s = Session()

@engine_blueprint.route('/api/tests', methods=['POST'])
def tests():
    data = request.json

    testsuite = db.testsuite.find_one({"_id":data.get("testsuite")["_id"]})
    res = []

    for i in testsuite['testcases']:
        testcase = db.testcases.find_one({"_id":i})
        if i in data.get('testcases'):
            testdata = db.testdata.find_one({"_id":data['testcases'][i]})
            
            testcase['payload']['payload'] = {**testcase['payload']['payload'], **testdata['payload']}
            testcase['payload']['expected_outcome'] = {**testcase['payload']['expected_outcome'], **testdata['expected_outcome']}
            
            res.append(perform_testcases(testcase))
    db.temp.find_one_and_delete({"project_id":testcase['project']})
    return jsonify(res)

def fetch_from_api(method, endpoint, data, header):
    r = Request(method, endpoint, json=data, headers=header)

    prepped = s.prepare_request(r)
    resp = s.send(prepped)

    return resp

def perform_testcases(testcase):

    header = testcase.get('endpoint').get("header_id").get("header")
    token = db.temp.find_one({"project_id":testcase['project']})
    if token:
        token = token.get('token')
        if "$token" in str(header) and token:
            header = str(header).replace("$token", token)
            header = eval(header)
            
    res = fetch_from_api(testcase['method'], testcase['endpoint']['endpoint'], testcase['payload']['payload'], header)

    if res.status_code==testcase['payload']['expected_outcome']['status_code']:

        if testcase.get("token_field"):
            tmp = testcase.get("token_field").split(".")

            token = res.json()
            for i in tmp:
                token = token.get(i)
            db.temp.insert_one({
                "_id": create_id(),
                "project_id": testcase['project'],
                "token": token
            })
        #db.results({"testcase_id":testcase['_id'], "title":testcase['title'], "status":"passed",**res.json()})
        return {"testcase_id":testcase['_id'], "title":testcase['title'], "status":"passed"}
    else:
        #db.results({"testcase_id":testcase['_id'], "title":testcase['title'], "status":"failed",**res.json()})
        return {"testcase_id":testcase['_id'], "title":testcase['title'], "status":"failed", **res.json()}
