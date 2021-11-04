import requests
import logging

from requests.adapters import HTTPAdapter

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
TIMEOUT = (1.0, 60.0)
HEADERS = {}


class Client(object):

    def __init__(self, url, api_key, session=None):
        """ Initialize client

        Parameters
        ----------
        url: str
            Label Studio host address, e.g.: http://localhost:8080
        api_key: str
            User token, you can find it on the account page
        session: requests.Session()
            If None, the new one will be created
        """
        self.url = url.rstrip('/')
        self.api_key = api_key
        self.session = session or self.get_session()

    def check_connection(self):
        """ Call Label Studio /health endpoint

        Returns
        -------
        dict
            Status string like "UP"
        """
        response = self.make_request('GET', '/health')
        return response.json()

    def start_project(self, **kwargs):
        """ Create new project instance

        Parameters
        ----------
        kwargs:
            Parameters for `project.start_project(**kwargs)`

        Returns
        -------
        class Project

        """
        from .project import Project
        project = Project(url=self.url, api_key=self.api_key, session=self.session)
        project.start_project(**kwargs)
        return project

    def get_project(self, id):
        """ Return project SDK object by ID

        Parameters
        ----------
        id

        Returns
        -------

        """
        from .project import Project
        return Project.get_from_id(self, id)

    # def create_project(self, *args, **kwargs):
    #     from .project import Project
    #     return Project(self, *args, **kwargs)
    #
    # def create_config(self, *args, **kwargs):
    #     from .label_config import LabelConfig
    #     return LabelConfig(self, *args, **kwargs)

    def get_session(self):
        """ Create a new requests.Session()

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
        return f'{self.url}/{suffix.lstrip("/")}'

    def make_request(self, method, url, *args, **kwargs):
        """ Make a request with API key to Label Studio instance

        Parameters
        ----------
        method: str
            HTTP method like POST, PATCH, GET, DELETE. etc
        url: str

        args
            session.request(*args)
        kwargs
            session.request(*kwargs)

        Returns
        -------
        Response object

        """
        if 'timeout' not in kwargs:
            kwargs['timeout'] = TIMEOUT
        logger.debug(f'{method}: {url} with args={args}, kwargs={kwargs}')
        headers = {'Authorization': f'Token {self.api_key}'}
        response = self.session.request(method, self.get_url(url), headers=headers, *args, **kwargs)
        response.raise_for_status()
        return response
