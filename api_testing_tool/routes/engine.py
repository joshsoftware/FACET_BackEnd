from requests import Request, Session
from flask import Blueprint, request, jsonify
from api_testing_tool import db

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
    return jsonify(res)

def fetch_from_api(method, endpoint, data):
    r = Request(method, endpoint, json=data, headers=s.headers)

    prepped = s.prepare_request(r)
    resp = s.send(prepped)

    return resp

def perform_testcases(testcase):
    res = fetch_from_api(testcase['method'], testcase['endpoint']['endpoint'], testcase['payload']['payload'])

    if res.status_code==testcase['payload']['expected_outcome']['status_code']:
        #db.results({"testcase_id":testcase['_id'], "title":testcase['title'], "status":"passed",**res.json()})
        return {"testcase_id":testcase['_id'], "title":testcase['title'], "status":"passed"}
    else:
        #db.results({"testcase_id":testcase['_id'], "title":testcase['title'], "status":"failed",**res.json()})
        return {"testcase_id":testcase['_id'], "title":testcase['title'], "status":"failed", **res.json()}

