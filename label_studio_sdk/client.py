""" .. include::../docs/client.md
"""
import warnings
import logging
import requests

from typing import Optional
from pydantic import BaseModel, constr, root_validator
from requests.adapters import HTTPAdapter

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
TIMEOUT = (1.0, 180.0)
HEADERS = {}


class ClientCredentials(BaseModel):
    email: Optional[str]
    password: Optional[str]
    api_key: Optional[constr()] = None

    @root_validator(pre=True, allow_reuse=True)
    def either_key_or_email_password(cls, values):
        assert 'email' in values or 'api_key' in values, 'At least one of email or api_key should be included'
        assert 'email' not in values or 'password' in values, 'Provide both email and password for login auth'
        return values


class Client(object):

    def __init__(self, url, api_key, credentials=None, session=None, extra_headers: dict = None, cookies: dict = None):
        """ Initialize the client. Do this before using other Label Studio SDK classes and methods in your script.

        Parameters
        ----------
        url: str
            Label Studio host address.
            Example: http://localhost:8080
        api_key: str
            User token for the API. You can find this on your user account page in Label Studio.
        credentials: ClientCredentials
            User email and password or api_key.
        session: requests.Session()
            If None, a new one is created.
        extra_headers: dict
            Additional headers that will be passed to each http request
        cookies: dict
            Cookies that will be passed to each http request.
        """
        self.url = url.rstrip('/')
        self.session = session or self.get_session()

        # set api key or get it using credentials (username and password)
        if api_key is not None:
            credentials = ClientCredentials(api_key=api_key)
        self.api_key = credentials.api_key if credentials.api_key else self.get_api_key(credentials)

        # set headers
        self.headers = {'Authorization': f'Token {self.api_key}'}
        if extra_headers:
            self.headers.update(extra_headers)

        # Set cookies
        self.cookies = cookies

    def get_api_key(self, credentials: ClientCredentials):
        login_url = self.get_url("/user/login")
        # Retrieve and set the CSRF token first
        self.session.get(login_url)
        csrf_token = self.session.cookies.get('csrftoken', None)
        login_data = dict(**credentials.dict(), csrfmiddlewaretoken=csrf_token)
        self.session.post(login_url, data=login_data, headers=dict(Referer=self.url), cookies=self.cookies).raise_for_status()
        api_key = self.session.get(self.get_url("/api/current-user/token")).json().get("token")
        return api_key

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

    def delete_project(self, project_id: int):
        """ Delete a project in Label Studio.

        Returns
        -------
        dict
            Status string
        """
        response = self.make_request('DELETE', f'/api/projects/{project_id}/')
        return response

    def delete_all_projects(self):
        """ Deletes all projects in Label Studio.

        Returns
        -------
        List
            List of (dict) status strings
        """
        responses = []
        project_ids = [project.get_params()['id'] for project in self.list_projects()]
        for project_id in project_ids:
            response = self.delete_project(project_id)
            responses.append(response)
        return responses

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
        response = self.session.request(method, self.get_url(url), headers=self.headers, cookies=self.cookies, *args, **kwargs)
        response.raise_for_status()
        return response

    def sync_storage(self, storage_type, storage_id):
        """Synchronize Cloud Storage.

        Parameters
        ----------
        storage_type: string
            Specify the type of the storage container.
        storage_id: int
            Specify the storage ID of the storage container.

        Returns
        -------
        dict:
            containing the same fields as in the original storage request and:

        id: int
            Storage ID
        type: str
            Type of storage
        created_at: str
            Creation time
        last_sync: str
            Time last sync finished, can be empty.
        last_sync_count: int
            Number of tasks synced in the last sync
        """

        response = self.make_request(
            "POST", f"/api/storages/{storage_type}/{str(storage_id)}/sync"
        )
        return response.json()
