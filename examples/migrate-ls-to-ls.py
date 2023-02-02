# Migration that copy projects from one LS instance to another
import time
import logging

from label_studio_sdk import Client
from label_studio_sdk.project import Project
from label_studio_sdk.users import User

logger = logging.getLogger('migration-ls-to-ls')


class Migration:
    def __init__(self, src_url, src_key, dst_url, dst_key):
        """ Initialize migration that copy projects from one LS instance to another

        :param src_url: source Label Studio instance
        :param src_key: source Label Studio token
        :param dst_url: destination Label Studio instance
        :param dst_key: destination Label Studio token
        """
        # Connect to the Label Studio API and check the connection
        self.src_ls = Client(url=src_url, api_key=src_key)
        self.dst_ls = Client(url=dst_url, api_key=dst_key)
        self.users = self.projects = self.project_ids = None

    @staticmethod
    def enable_logging():
        logging.basicConfig(level=logging.DEBUG)

    def set_project_ids(self, project_ids=None):
        """ Set projects you need to migrate

        :param project_ids: List of project ids to copy, set None if you need to copy all projects
        """
        self.project_ids = project_ids

    def run(self, project_ids=None):
        projects = self.get_projects(project_ids)
        users = self.get_users(projects)
        self.create_users(users)

    def get_projects(self, project_ids):
        # get project by project ids
        self.project_ids = project_ids
        if self.project_ids is None:
            self.projects = self.src_ls.get_projects()
        else:
            self.projects = [self.src_ls.get_project(id=pid) for pid in self.project_ids]

        return self.projects

    def get_users(self, projects: [Project]) -> [User]:
        """ Get users that are members of all projects
        """
        users = {}
        for project in projects:
            members = project.get_members()
            id_members = {member.id: member for member in members}
            logger.debug(f'Get {len(members)} users from project {project.id}')
            users.update(id_members)

        self.users = list(users.values())
        return self.users

    def create_users(self, users: [User]):
        logger.debug(f'Going to create {len(users)} users on {self.dst_ls}')
        new_users = []
        for user in users:
            new_user = self.dst_ls.create_user(user)
            if new_user is not None:
                new_users.append(new_user)
                logger.debug(f'User {new_user.email} created')
        logger.debug(f'{len(new_users)} users created, total {len(users)} users')
        logger.debug(f'Created users: {[u.email for u in new_users]}')
        return new_users

    def export_snapshot(self, project):
        """ Export all tasks from the project
        """
        # create new export snapshot
        export_result = project.export_snapshot_create(title='Migration snapshot')
        assert ('id' in export_result)
        export_id = export_result['id']

        # wait until snapshot is ready
        while project.export_snapshot_status(export_id).is_in_progress():
            time.sleep(1.0)

        # download snapshot file
        status, file_name = project.export_snapshot_download(export_id, export_type='JSON')
        assert (status == 200)
        assert (file_name is not None)
        logger.debug(f"Status of the export is {status}. File name is {file_name}")
        return status, file_name


def run():
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='Label Studio Project Migration Script')
    parser.add_argument(
        '--src-url',
        dest='src_url',
        type=str,
        default='',
        help='Source Label Studio instance'
    )
    parser.add_argument(
        '--src-key',
        dest='src_key',
        type=str,
        default='',
        help='Source Label Studio token, it should be owner or administrator token'
    )
    parser.add_argument(
        '--dst-url',
        dest='dst_url',
        type=str,
        default='',
        help='Destination Label Studio instance'
    )
    parser.add_argument(
        '--dst-key',
        dest='dst_key',
        type=str,
        default='',
        help='Destination Label Studio token, it should be owner or administrator token'
    )
    parser.add_argument(
        '--project-ids',
        dest='project_ids',
        type=str,
        default=None,
        help='Project ids separated by comma, e.g.: 54,78,98'
    )
    args = parser.parse_args(sys.argv[1:])

    migration = Migration(
        src_url=args.src_url,
        src_key=args.src_key,
        dst_url=args.dst_url,
        dst_key=args.dst_key
    )
    migration.enable_logging()

    project_ids = [int(i) for i in args.project_ids.split(',')] if args.project_ids else None
    migration.run(project_ids)


if __name__ == '__main__':
    run()
