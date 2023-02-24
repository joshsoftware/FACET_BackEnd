"""
Load testing script for FACET application using `locust` library.
"""
import random
from locust import HttpUser, between, task, TaskSet

# Create a project by generating random name and delete it in on_stop function
class ProjectsTaskSet(TaskSet):
    """
    TaskSet class for performing load testing on the Projects API endpoints.
    """
    project_name = None
    testcases = []
    environments = []

    def on_start(self):
        """
        Called when a Locust user starts. Gets the name of a random project
        and stores it in the `project_name` attribute.
        """
        response = self.client.get("/api/projects", headers=self.user.headers)
        projects = response.json().get("projects")
        self.project_name = projects[0].get("name")

    @task
    def get_environments(self):
        """
        Performs a GET request on the Environments endpoint with the
        project_name parameter. Stores the list of environment IDs in
        the `environments` attribute.
        """
        params = {"project": self.project_name}
        with self.client.get(
            "/api/environments", params=params, headers=self.user.headers
        ) as response:
            environments = response.json().get("environments")
            if environments:
                self.environments = [env.get("id") for env in environments]

    @task
    def get_endpoints(self):
        """
        Performs a GET request on the Endpoints endpoint with the
        project_name parameter.
        """
        params = {"project": self.project_name}
        self.client.get("/api/endpoints", params=params, headers=self.user.headers)

    @task
    def get_headers(self):
        """
        Performs a GET request on the Headers endpoint with the
        project_name parameter.
        """
        params = {"project": self.project_name}
        self.client.get("/api/headers", params=params, headers=self.user.headers)

    @task
    def get_payloads(self):
        """
        Performs a GET request on the Payloads endpoint with the
        project_name parameter.
        """
        params = {"project": self.project_name}
        self.client.get("/api/payloads", params=params, headers=self.user.headers)

    @task
    def get_teststeps(self):
        """
        Performs a GET request on the Teststeps endpoint with the
        project_name parameter.
        """
        params = {"project": self.project_name}
        self.client.get("/api/teststeps", params=params, headers=self.user.headers)

    @task
    def get_testcases(self):
        """
        Performs a GET request on the Testcases endpoint with the
        project_name parameter. Stores the list of testcase IDs in
        the `testcases` attribute.
        """
        params = {"project": self.project_name}
        with self.client.get(
            "/api/testcases", params=params, headers=self.user.headers
        ) as testcases:
            if testcases.json().get("testcases"):
                self.testcases = [
                    tc.get("id") for tc in testcases.json().get("testcases")
                ]

    @task
    def get_testsuites(self):
        """
        Performs a GET request on the Testsuites endpoint with the
        project_name parameter.
        """
        params = {"project": self.project_name}
        self.client.get("/api/testsuites", params=params, headers=self.user.headers)

    @task
    def execute_testcases(self):
        """
        Performs a POST request on the Tests endpoint with a random
        environment ID and a random testcase ID.
        """
        if len(self.environments) and len(self.testcases):
            payload = {
                "environment": random.choice(self.environments),
                "level": "testcase",
                "testcase": random.choice(self.testcases),
            }
            self.client.post("/api/tests", headers=self.user.headers, json=payload)


class MyUser(HttpUser):
    """
    HttpUser class for FACET load testing
    A class representing a user that will simulate user behavior in a load test scenario.
    """
    wait_time = between(1, 2)
    tasks = [ProjectsTaskSet]
    headers = {}

    def on_start(self):
        """
        Called when a Locust user starts.
        A method that logs the user in to the FACET application and sets the `Authorization` header.
        """
        response = self.client.post(
            "/api/auth/login",
            json={"email": "superadmin@facet.com", "password": "admin"},
        )
        self.headers = {
            "Authorization": f"Bearer {response.json().get('access_token')}"
        }
