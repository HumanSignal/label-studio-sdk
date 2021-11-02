import requests
import logging

from requests.adapters import HTTPAdapter

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
TIMEOUT = (1.0, 60.0)
HEADERS = {}


class Client(object):

    def __init__(self, url, api_key, session=None):
        self.url = url.rstrip('/')
        self.api_key = api_key
        self.session = session or self.get_session()

    def check_connection(self):
        response = self.make_request('GET', '/health')
        return response.json()

    def start_project(self, **kwargs):
        from .project import Project
        project = Project(url=self.url, api_key=self.api_key, session=self.session)
        project.start_project(**kwargs)
        return project

    def get_project(self, id):
        """
        Return project SDK object by ID
        :param id:
        :return:
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
        session = requests.Session()
        session.headers.update(HEADERS)
        session.mount('http://', HTTPAdapter(max_retries=MAX_RETRIES))
        session.mount('https://', HTTPAdapter(max_retries=MAX_RETRIES))
        return session

    def get_url(self, suffix):
        return f'{self.url}/{suffix.lstrip("/")}'

    def make_request(self, method, url, *args, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = TIMEOUT
        logger.debug(f'{method}: {url} with args={args}, kwargs={kwargs}')
        headers = {'Authorization': f'Token {self.api_key}'}
        response = self.session.request(method, self.get_url(url), headers=headers, *args, **kwargs)
        response.raise_for_status()
        return response
