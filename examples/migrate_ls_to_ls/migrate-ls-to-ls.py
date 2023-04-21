""" This migration helps to copy projects from one LS instance to another.

Usage:
> python3 migrate-ls-to-ls.py --src-url src-ls.com --src-key <src-token> --dst-url dst-ls.com --dst-key <dst-token> --project-ids=123,456
"""
import os
import time
import json
import logging

from label_studio_sdk import Client
from label_studio_sdk.project import Project
from label_studio_sdk.users import User

logger = logging.getLogger('migration-ls-to-ls')


class Migration:
    def __init__(self, src_url, src_key, dst_url, dst_key):
        """Initialize migration that copy projects from one LS instance to another

        :param src_url: source Label Studio instance
        :param src_key: source Label Studio token
        :param dst_url: destination Label Studio instance
        :param dst_key: destination Label Studio token
        """
        # Connect to the Label Studio API and check the connection
        self.src_ls = Client(url=src_url, api_key=src_key)
        self.dst_ls = Client(url=dst_url, api_key=dst_key)
        self.users = self.projects = self.project_ids = None

    def set_project_ids(self, project_ids=None):
        """Set projects you need to migrate

        :param project_ids: List of project ids to copy, set None if you need to copy all projects
        """
        self.project_ids = project_ids

    def run(self, project_ids=None):
        projects = self.get_projects(project_ids)
        users = self.get_users(projects)
        self.create_users(users)

        # start exporting projects
        for project in projects:
            logger.info(
                f'Going to create export snapshot for project {project.id} {project.params["title"]}'
            )
            status, filename = self.export_snapshot(project)
            logger.info(
                f'Snapshot for project {project.id} created with status {status} and filename {filename}'
            )
            self.patch_snapshot_users(filename)

            if status != 200:
                logger.info(f'Skipping project {project.id} because of errors {status}')
                continue

            new_project = self.create_project(project)

            logger.info(f'Going to import {filename} to project {new_project.id}')
            new_project.import_tasks(filename)
            logger.info(f'Import {filename} finished for project {new_project.id}')

        logger.info('All projects are processed, finish')

    def create_project(self, project):
        logger.info(
            f'Going to create a new project "{project.params["title"]}" from old project {project.id}'
        )
        copied_fields = {
            'title',
            'description',
            'label_config',
            'expert_instruction',
            'show_instruction',
            'show_skip_button',
            'enable_empty_annotation',
            'show_annotation_history',
            'color',
            'maximum_annotations',
            'is_published',
            'model_version',
            'is_draft',
            'min_annotations_to_start_training',
            'start_training_on_annotation_update',
            'show_collab_predictions',
            'sampling',
            'show_ground_truth_first',
            'show_overlap_first',
            'overlap_cohort_percentage',
            'task_data_login',
            'task_data_password',
            'control_weights',
            'parsed_label_config',
            'evaluate_predictions_automatically',
            'config_has_control_tags',
            'skip_queue',
            'reveal_preannotations_interactively',
            'require_comment_on_skip',
        }
        params = {
            field: project.params[field]
            for field in project.params
            if field in copied_fields
        }
        new_project = self.dst_ls.start_project(**params)
        self.read_and_update_project_mapping(project, new_project)
        logger.info(
            f'New project {new_project.id} {new_project.params["title"]} is created'
        )
        return new_project

    @staticmethod
    def read_and_update_project_mapping(old_project, new_project):
        """Project mapping for ids: old project id => new project id"""
        mapping = {}
        path = 'project_mapping.json'
        if os.path.exists(path):
            with open(path, 'r') as f:
                mapping = json.load(f)

        mapping[old_project.id] = new_project.id

        with open(path, 'w') as f:
            json.dump(mapping, f)
        logger.info(f'{path} is updated')
        return mapping

    def get_projects(self, project_ids):
        # get project by project ids
        self.project_ids = project_ids
        if self.project_ids is None:
            self.projects = self.src_ls.get_projects()
        else:
            self.projects = [
                self.src_ls.get_project(id=pid) for pid in self.project_ids
            ]

        return self.projects

    def get_users(self, projects: [Project]) -> [User]:
        """Get users that are members of all projects at the source instance"""
        # enterprise instance
        if self.src_ls.is_enterprise:
            users = {}
            for project in projects:
                members = project.get_members()
                id_members = {member.id: member for member in members}
                logger.info(f'Get {len(members)} users from project {project.id}')
                users.update(id_members)

            self.users = list(users.values())

        # community instance doesn't have per-project members, all users have access to all projects
        else:
            self.users = self.src_ls.get_users()

        return self.users

    def create_users(self, users: [User]):
        logger.info(
            f'Going to create {len(users)} users on {self.dst_ls}. '
            f'It is normal to see errors here if a user already exists.'
        )
        new_users = []
        for user in users:
            new_user = self.dst_ls.create_user(user)
            if new_user is not None:
                new_users.append(new_user)
                logger.info(f'User {new_user.email} created')
        logger.info(f'{len(new_users)} users created, total {len(users)} users')
        logger.info(f'Created users: {[u.email for u in new_users]}')
        return new_users

    def export_snapshot(self, project):
        """Export all tasks from the project"""
        # create new export snapshot
        export_result = project.export_snapshot_create(
            title='Migration snapshot',
            serialization_options_annotations__completed_by=False,
        )
        assert 'id' in export_result
        export_id = export_result['id']

        # wait until snapshot is ready
        while project.export_snapshot_status(export_id).is_in_progress():
            time.sleep(1.0)

        # download snapshot file
        status, file_name = project.export_snapshot_download(
            export_id, export_type='JSON'
        )
        assert status == 200
        assert file_name is not None
        logger.info(f"Status of the export is {status}. File name is {file_name}")
        return status, file_name

    def patch_snapshot_users(self, filename):
        """
        Community LS versions export completed_by as int instead of dict with email,
        this patch converts int to dict with email in all annotations

        :param filename: path to json snapshot
        :returns rewrite source file with the patched version of json snapshot
        """
        # LSE versions don't need this patch
        if self.src_ls.is_enterprise:
            return

        id_users = {user.id: user for user in self.users}

        with open(filename, 'r', encoding='utf8') as f:
            tasks = json.load(f)

        for task in tasks:
            for annotation in task['annotations']:
                user = annotation['completed_by']
                if isinstance(user, int):
                    annotation['completed_by'] = {
                        "id": user,
                        'email': id_users[user].email,
                    }
                else:
                    return  # completed_by is not int, exiting

        with open(filename, 'w') as out:
            json.dump(tasks, out)

        logger.info(f'Completed_by patch is applied to {filename}')


def run():
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description='Label Studio Project Migration Script'
    )
    parser.add_argument(
        '--src-url',
        dest='src_url',
        type=str,
        default='',
        help='Source Label Studio instance',
    )
    parser.add_argument(
        '--src-key',
        dest='src_key',
        type=str,
        default='',
        help='Source Label Studio token, it should be owner or administrator token',
    )
    parser.add_argument(
        '--dst-url',
        dest='dst_url',
        type=str,
        default='',
        help='Destination Label Studio instance',
    )
    parser.add_argument(
        '--dst-key',
        dest='dst_key',
        type=str,
        default='',
        help='Destination Label Studio token, it should be owner or administrator token',
    )
    parser.add_argument(
        '--project-ids',
        dest='project_ids',
        type=str,
        default=None,
        help='Project ids separated by comma, e.g.: 54,78,98',
    )
    args = parser.parse_args(sys.argv[1:])

    migration = Migration(
        src_url=args.src_url,
        src_key=args.src_key,
        dst_url=args.dst_url,
        dst_key=args.dst_key,
    )
    logging.basicConfig(level=logging.INFO)

    project_ids = (
        [int(i) for i in args.project_ids.split(',')] if args.project_ids else None
    )
    migration.run(project_ids)


if __name__ == '__main__':
    run()
