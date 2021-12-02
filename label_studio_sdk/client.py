""" .. include::../docs/client.md
"""
import requests
import logging

from requests.adapters import HTTPAdapter

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
TIMEOUT = (1.0, 60.0)
HEADERS = {}


class Client(object):

    def __init__(self, url, api_key, session=None):
        """ Initialize the client. Do this before using other Label Studio SDK classes and methods in your script.

        Parameters
        ----------
        url: str
            Label Studio host address.
            Example: http://localhost:8080
        api_key: str
            User token for the API. You can find this on your user account page in Label Studio.
        session: requests.Session()
            If None, a new one is created.
        """
        self.url = url.rstrip('/')
        self.api_key = api_key
        self.session = session or self.get_session()

    def check_connection(self):
        """ Call Label Studio /health endpoint to check the connection to the server.

        Returns
        -------
        dict
            Status string like "UP"
        """
        response = self.make_request('GET', '/health')
        return response.json()

    def get_projects(self):
        """ List all projects in Label Studio.

        Returns
        -------
        list or `label_studio_sdk.project.Project` instances

        """
        return self.list_projects()

    def list_projects(self):
        """ List all projects in Label Studio.

        Returns
        -------
        list or `label_studio_sdk.project.Project` instances

        """
        from .project import Project
        response = self.make_request('GET', '/api/projects', params={'page_size': 10000000})
        if response.status_code == 200:
            projects = []
            for data in response.json()['results']:
                projects.append(Project._create_from_id(client=self, project_id=data['id'], params=data))
            return projects

    def start_project(self, **kwargs):
        """ Create a new project instance.

        Parameters
        ----------
        kwargs:
            Parameters for `project.start_project(**kwargs)`

        Returns
        -------
        `label_studio_sdk.project.Project`

        """
        from .project import Project
        project = Project(url=self.url, api_key=self.api_key, session=self.session)
        project.start_project(**kwargs)
        return project

    def get_project(self, id):
        """ Return project SDK object by ID existed in Label Studio

        Parameters
        ----------
        id: int
            Project ID for the project you want to retrieve.

        Returns
        -------
        `label_studio_sdk.project.Project`

        """
        from .project import Project
        return Project.get_from_id(self, id)

    def get_users(self):
        """ Return all users from the current organization account

        Parameters
        ----------

        Returns
        -------
        list of `label_studio_sdk.users.User`

        """
        from .users import User
        response = self.make_request('GET', '/api/users')
        users = []
        for user_data in response.json():
            user_data['client'] = self
            users.append(User(**user_data))
        return users

    def get_workspaces(self):
        """ Return all workspaces from the current organization account

        Parameters
        ----------

        Returns
        -------
        list of `label_studio_sdk.workspaces.Workspace`

        """
        from .workspaces import Workspace
        response = self.make_request('GET', '/api/workspaces')
        workspaces = []
        for workspace_data in response.json():
            workspace_data['client'] = self
            workspaces.append(Workspace(**workspace_data))
        return workspaces

    def get_session(self):
        """ Create a session with requests.Session()

        Returns
        -------
        request.Session

        """
        session = requests.Session()
        session.headers.update(HEADERS)
        session.mount('http://', HTTPAdapter(max_retries=MAX_RETRIES))
        session.mount('https://', HTTPAdapter(max_retries=MAX_RETRIES))
        return session

    def get_url(self, suffix):
        """ Get the URL of the Label Studio server

        Returns
        -------
        String with the URL

        """
        return f'{self.url}/{suffix.lstrip("/")}'

    def make_request(self, method, url, *args, **kwargs):
        """ Make a request with an API key to Label Studio instance

        Parameters
        ----------
        method: str
            HTTP method like POST, PATCH, GET, DELETE.
        url: str
            URL of the API endpoint that you want to make a request to.

        args
            session.request(*args)
        kwargs
            session.request(*kwargs)

        Returns
        -------
        Response object for the relevant endpoint.

        """
        if 'timeout' not in kwargs:
            kwargs['timeout'] = TIMEOUT
        logger.debug(f'{method}: {url} with args={args}, kwargs={kwargs}')
        headers = {'Authorization': f'Token {self.api_key}'}
        response = self.session.request(method, self.get_url(url), headers=headers, *args, **kwargs)
        response.raise_for_status()
        return response
