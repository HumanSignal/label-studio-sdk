""" .. include::../docs/client.md
"""

import json
import logging
import os

import requests

from typing import Optional
from pydantic import BaseModel, constr, root_validator
from requests.adapters import HTTPAdapter

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
TIMEOUT = (10.0, int(os.environ.get('TIMEOUT', 180)))
HEADERS = {}
LABEL_STUDIO_DEFAULT_URL = "http://localhost:8080"


class ClientCredentials(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[constr()] = None

    @root_validator(pre=True, allow_reuse=True)
    def either_key_or_email_password(cls, values):
        assert (
            "email" in values or "api_key" in values
        ), "At least one of email or api_key should be included"
        assert (
            "email" not in values or "password" in values
        ), "Provide both email and password for login auth"
        return values


class Client(object):
    def __init__(
        self,
        url: str = None,
        api_key: str = None,
        credentials=None,
        session=None,
        extra_headers: dict = None,
        cookies: dict = None,
        oidc_token=None,
        versions=None,
        make_request_raise=True,
    ):
        """Initialize the client. Do this before using other Label Studio SDK classes and methods in your script.

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
        oidc_token: str
            Bearer token for proxy authentication - in case the server is behind an authenticating proxy.
        versions: dict
            Versions of Label Studio components for the connected instance
        make_request_raise: bool
            If true, make_request will raise exceptions on request errors
        """
        if not url:
            url = os.getenv("LABEL_STUDIO_URL", LABEL_STUDIO_DEFAULT_URL)
        self.url = url.rstrip("/")
        self.make_request_raise = make_request_raise
        self.session = session or self.get_session()

        # set cookies
        self.cookies = cookies

        # set api key or get it using credentials (username and password)
        if api_key is None and credentials is None:
            api_key = os.getenv("LABEL_STUDIO_API_KEY")

        if api_key is not None:
            credentials = ClientCredentials(api_key=api_key)

        if api_key is None and credentials is None:
            raise RuntimeError(
                "If neither 'api_key' nor 'credentials' are provided, 'LABEL_STUDIO_API_KEY' environment variable must "
                "be set"
            )

        self.api_key = (
            credentials.api_key
            if credentials.api_key
            else self.get_api_key(credentials)
        )

        # set headers
        self.headers = {"Authorization": f"Token {self.api_key}"}
        if oidc_token:
            self.headers.update({"Proxy-Authorization": f"Bearer {oidc_token}"})
        if extra_headers:
            self.headers.update(extra_headers)

        # set versions from /version endpoint
        self.versions = versions if versions else self.get_versions()
        self.is_enterprise = "label-studio-enterprise-backend" in self.versions

    def get_versions(self):
        """Call /version api and get all Label Studio component versions

        Returns
        -------
        dict with Label Studio component names and their versions

        """
        self.versions = self.make_request("GET", "/api/version").json()
        return self.versions

    def get_api_key(self, credentials: ClientCredentials):
        login_url = self.get_url("/user/login")
        # Retrieve and set the CSRF token first
        self.session.get(login_url)
        csrf_token = self.session.cookies.get("csrftoken", None)
        login_data = dict(**credentials.dict(), csrfmiddlewaretoken=csrf_token)
        self.session.post(
            login_url,
            data=login_data,
            headers=dict(Referer=self.url),
            cookies=self.cookies,
        ).raise_for_status()
        api_key = (
            self.session.get(self.get_url("/api/current-user/token"))
            .json()
            .get("token")
        )
        return api_key

    def check_connection(self):
        """Call Label Studio /health endpoint to check the connection to the server.

        Returns
        -------
        dict
            Status string like "UP"
        """
        response = self.make_request("GET", "/health")
        return response.json()

    def get_projects(self, **query_params):
        """List all projects in Label Studio.

        Returns
        -------
        list or `label_studio_sdk.project.Project` instances

        """
        return self.list_projects(**query_params)

    def delete_project(self, project_id: int):
        """Delete a project in Label Studio.

        Returns
        -------
        dict
            Status string
        """
        response = self.make_request("DELETE", f"/api/projects/{project_id}/")
        return response

    def delete_all_projects(self):
        """Deletes all projects in Label Studio.

        Returns
        -------
        List
            List of (dict) status strings
        """
        responses = []
        project_ids = [project.get_params()["id"] for project in self.list_projects()]
        for project_id in project_ids:
            response = self.delete_project(project_id)
            responses.append(response)
        return responses

    def list_projects(self, **query_params):
        """List all projects in Label Studio.

        Returns
        -------
        list or `label_studio_sdk.project.Project` instances

        """
        from .project import Project

        params = {"page_size": 10000000}
        params.update(query_params)
        response = self.make_request("GET", "/api/projects", params=params)
        if response.status_code == 200:
            projects = []
            for data in response.json()["results"]:
                project = Project._create_from_id(
                    client=self, project_id=data["id"], params=data
                )
                projects.append(project)
                logger.debug(
                    f'Project {project.id} "{project.get_params().get("title")}" is retrieved'
                )
            return projects

    def create_project(self, **kwargs):
        return self.start_project(**kwargs)

    def start_project(self, **kwargs):
        """Create a new project instance.

        Parameters
        ----------
        kwargs:
            Parameters for `project.start_project(**kwargs)`

        Returns
        -------
        `label_studio_sdk.project.Project`

        """
        from .project import Project

        project = Project(
            url=self.url,
            api_key=self.api_key,
            session=self.session,
            versions=self.versions,
        )
        project.start_project(**kwargs)
        return project

    def get_project(self, id):
        """Return project SDK object by ID existed in Label Studio

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
        """Return all users from the current organization account

        Parameters
        ----------

        Returns
        -------
        list of `label_studio_sdk.users.User`

        """
        from .users import User

        response = self.make_request("GET", "/api/users")
        users = []
        for user_data in response.json():
            user_data["client"] = self
            users.append(User(**user_data))
        return users

    def create_user(self, user, exist_ok=True):
        """Create a new user

        Parameters
        ----------
        user: User or dict
            User instance, you can initialize it this way:
            User(username='x', email='x@x.xx', first_name='X', last_name='Z')
        exist_ok: bool
            True by default, it won't print error if user exists and exist_ok=True

        Returns
        -------
        `label_studio_sdk.users.User`
            Created user

        """
        from .users import User

        payload = (
            {
                "username": user.username if user.username else user.email,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": user.phone,
            }
            if isinstance(user, User)
            else user
        )

        response = self.make_request(
            "POST", "/api/users", json=payload, raise_exceptions=False
        )
        user_data = response.json()
        user_data["client"] = self

        if response.status_code < 400:
            return User(**user_data)
        else:
            if "already exists" in response.text and exist_ok is True:
                return None
            logger.error("Create user error: " + str(response.json()))
            return None

    def get_workspaces(self):
        """Return all workspaces from the current organization account

        Parameters
        ----------

        Returns
        -------
        list of `label_studio_sdk.workspaces.Workspace`

        """
        from .workspaces import Workspace

        assert (
            self.is_enterprise
        ), "Workspaces are available only for Enterprise instance of Label Studio"

        response = self.make_request("GET", "/api/workspaces")
        workspaces = []
        for workspace_data in response.json():
            workspace_data["client"] = self
            workspaces.append(Workspace(**workspace_data))
        return workspaces

    # write function get_workspace_by_title
    def get_workspace_by_title(self, title):
        """Return workspace by title from the current organization account

        Parameters
        ----------
        title: str
            Workspace title

        Returns
        -------
        `label_studio_sdk.workspaces.Workspace` or None

        """
        workspaces = self.get_workspaces()
        for workspace in workspaces:
            if workspace.title == title:
                return workspace
        return None

    def get_organization(self):
        """Return active organization for the current user

        Returns
        -------
        dict
        """
        # get organization id from the current user api
        response = self.make_request('GET', '/api/current-user/whoami').json()
        organization_id = response['active_organization']

        # get organization data by id
        response = self.make_request("GET", f"/api/organizations/{organization_id}")
        return response.json()

    def get_session(self):
        """Create a session with requests.Session()

        Returns
        -------
        request.Session

        """
        session = requests.Session()
        session.headers.update(HEADERS)
        session.mount("http://", HTTPAdapter(max_retries=MAX_RETRIES))
        session.mount("https://", HTTPAdapter(max_retries=MAX_RETRIES))
        return session

    def get_url(self, suffix):
        """Get the URL of the Label Studio server

        Returns
        -------
        String with the URL

        """
        return f'{self.url}/{suffix.lstrip("/")}'

    def make_request(self, method, url, *args, **kwargs):
        """Make a request with an API key to Label Studio instance

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
        if "timeout" not in kwargs:
            kwargs["timeout"] = TIMEOUT

        raise_exceptions = self.make_request_raise
        if "raise_exceptions" in kwargs:  # kwargs have higher priority
            raise_exceptions = kwargs.pop("raise_exceptions")

        logger.debug(f"{method}: {url} with args={args}, kwargs={kwargs}")
        response = self.session.request(
            method,
            self.get_url(url),
            headers=self.headers,
            cookies=self.cookies,
            *args,
            **kwargs,
        )

        if raise_exceptions:
            if response.status_code >= 400:
                self.log_response_error(response)
                response.raise_for_status()

        return response

    def log_response_error(self, response):
        try:
            content = json.dumps(json.loads(response.content), indent=2)
        except:
            content = response.text

        logger.error(
            f"\n--------------------------------------------\n"
            f"Request URL: {response.url}\n"
            f"Response status code: {response.status_code}\n"
            f"Response content:\n{content}\n\n"
            f"SDK error traceback:"
        )

    def sync_storage(self, storage_type, storage_id):
        """See project.sync_storage for more info"""
        response = self.make_request(
            "POST", f"/api/storages/{storage_type}/{str(storage_id)}/sync"
        )
        return response.json()
