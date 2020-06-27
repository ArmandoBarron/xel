
from requests.exceptions import ConnectionError

import requests
from requests.exceptions import MissingSchema


# Perform the communication with the dagon service
class API:
    def __init__(self, url):
        self.base_url = url
        self.checkConnection()

    # check if the service URL is valid or a service is available
    def checkConnection(self):
        """
        check if the service URL is valid or a service is available

        :raises ConnectionError: when it's not possible to connect to the URL provided
        """
        try:
            requests.head(self.base_url)
        except ConnectionError as e:
            raise ConnectionError("It is not possible connect to the URL %s" % self.base_url)
        except MissingSchema:
            raise ConnectionError("Bad URL %s" % self.base_url)

    # create workflow on dagon service
    def create_workflow(self, workflow):
        """
        create workflow on dagon service

        :param workflow: :class:`dagon.Workflow` object to save
        :type workflow: :class:`dagon.Workflow`

        :return: workflow id
        :rtype: int

        :raises Exception: when there is an error with the registration or the workflow name already exists
        """
        service = "/create"
        url = self.base_url + service
        data = workflow.as_json()
        res = requests.post(url, json=data)
        if res.status_code == 201:  # created
            json_reponse = res.json()
            return json_reponse['id']
        else:
            if res.status_code == 409:
                raise Exception("Workflow name already exists %d %s" % (res.status_code, res.reason))
            else:
                raise Exception("Workflow error registration %d %s" % (res.status_code, res.reason))

    # add task to workflow
    def add_task(self, workflow_id, task):
        """
        add task to workflow

        :param workflow_id: workflow id of the tasks
        :type workflow_id: int

        :param task: task to add to the workflow
        :type task: :class:`dagon.task.Task`

        :raises Exception: when there is an error with the call
        """
        service = "/add_task/%s" % workflow_id
        url = self.base_url + service
        data = task.as_json()
        res = requests.post(url, json=data)
        if res.status_code != 201 and res.status_code != 200:  # error
            raise Exception("Something went wrong %d %s" % (res.status_code, res.reason))

    # update a task status in the server
    def update_task_status(self, workflow_id, task, status):
        """
        update a task status in the server

        :param workflow_id: workflow id of the tasks
        :type workflow_id: int

        :param task: name of the task
        :type task: str

        :param status: task status
        :type status: str

        :raises Exception: when there is an error with the call
        """
        service = "/changestatus/%s/%s/%s" % (workflow_id, task, status)
        url = self.base_url + service
        res = requests.put(url)
        if res.status_code != 201 and res.status_code != 200:  # error
            raise Exception("Something went wrong %d %s" % (res.status_code, res.reason))

    # get a task from the server
    def get_task(self, workflow_name, task):
        """
        get a task from the server

        :param workflow_id: workflow id of the tasks
        :type workflow_id: int

        :param task: name of the task
        :type task: str

        :return: task
        :rtype: :class:`dagon.task.Task`

        :raises Exception: when there is an error with the call
        """
        workflow_id = self.get_workflow(workflow_name)['id']
        service = "/%s/%s" % (workflow_id, task)
        url = self.base_url + service
        res = requests.get(url)
        if res.status_code != 201 and res.status_code != 200:  # error
            raise Exception("Something went wrong %s %s" % (workflow_id, res.reason))
        else:
            task = res.json()
            return task


    # get a task from the server
    def get_workflow_by_id(self, workflow_id):
        """
        get a workflow from the server

        :param workflow_name: workflow name
        :type workflow_name: str

        :return: id
        :rtype: :str

        :raises Exception: when there is an error with the call
        """

        service = "/%s" % workflow_id
        url = self.base_url + service
        res = requests.get(url)
        if res.status_code != 201 and res.status_code != 200:  # error
            raise Exception("Something went wrong, no Transversal workflow %s founded, %d %s" % (workflow_id,res.status_code, res.reason))
        else:
            workflow = res.json()
            return workflow


    def get_workflow(self, workflow_name):
        """
        get a workflow from the server

        :param workflow_name: workflow name
        :type workflow_name: str

        :return: id
        :rtype: :str

        :raises Exception: when there is an error with the call
        """
        workflow_id = self.get_workflow_by_name(workflow_name)
        service = "/%s" % workflow_id
        url = self.base_url + service
        res = requests.get(url)
        if res.status_code != 201 and res.status_code != 200:  # error
            raise Exception("Something went wrong, no Transversal workflow %s founded, %d %s" % (workflow_id,res.status_code, res.reason))
        else:
            workflow = res.json()
            return workflow
    # get a task from the server
    def get_workflow_by_name(self, workflow_name):
        """
        get a workflow id from the server

        :param workflow_name: workflow name
        :type workflow_name: str

        :return: id
        :rtype: :str

        :raises Exception: when there is an error with the call
        """

        service = "/getworkflow/%s" % workflow_name
        url = self.base_url + service
        res = requests.get(url)
        if res.status_code != 201 and res.status_code != 200:  # error
            raise Exception("Something went wrong, no Transversal workflow %s founded, %d %s" % (workflow_name,res.status_code, res.reason))
        else:
            workflow_id = res.text
            return workflow_id

    # update atribute of the task
    def update_task(self, workflow_id, task, attribute, value):
        """
        update attribute of the task

        :param workflow_id: workflow id of the tasks
        :type workflow_id: int

        :param task: name of the task
        :type task: str

        :param attribute: attribute of the task to update
        :type task: str

        :param value: value of the attribute
        :type task: str

        :raises Exception: when there is an error with the call
        """

        service = "/update/%s/%s/%s?value=%s" % (workflow_id, task, attribute, value)
        url = self.base_url + service
        res = requests.put(url)
        if res.status_code != 201 and res.status_code != 200:  # error
            raise Exception("Something went wrong %d %s" % (res.status_code, res.reason))

    # add dependency on task
    def add_dependency(self, workflow_id, task, dependency):
        """
        add a dependency to an existing task in a workflow

        :param workflow_id: workflow id of the tasks
        :type workflow_id: int

        :param task: name of the task
        :type task: str

        :param dependency: name of the dependency
        :type task: str

        :raises Exception: when there is an error with the call
        """
        service = "/%s/%s/dependency/%s" % (workflow_id, task, dependency)
        url = self.base_url + service
        res = requests.put(url)
        if res.status_code != 201 and res.status_code != 200:  # error
            raise Exception("Something went wrong %d %s" % (res.status_code, res.reason))
