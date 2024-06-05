""" Migrate LS to LS script.
This migration helps to copy projects from one LS instance to another.

Usage:
> python3 migrate-ls-to-ls.py --src-url src-ls.com --src-key <src-token> --dst-url dst-ls.com --dst-key <dst-token> --project-ids=123,456
"""

import json
import logging
import os
import time

from label_studio_sdk import Client
from label_studio_sdk.data_manager import Filters, Operator, Type, Column
from label_studio_sdk.users import User

logger = logging.getLogger("migration-ls-to-ls")
logger.setLevel(logging.DEBUG)

CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', 1000))
DEFAULT_STORAGE = os.getenv('DEFAULT_STORAGE', '')  # 's3', 'gcs' or 'azure'
DEFAULT_STORAGE_REGEX = os.getenv(
    'DEFAULT_STORAGE_REGEX', '.*'
)  # regex for file search
DEFAULT_STORAGE_BUCKET = os.getenv('DEFAULT_STORAGE_BUCKET', 'bucket')  # bucket
DEFAULT_STORAGE_PREFIX = os.getenv('DEFAULT_STORAGE_PREFIX', '')  # prefix
DEFAULT_STORAGE_NAME = os.getenv('DEFAULT_STORAGE_NAME', '')  # azure key
DEFAULT_STORAGE_KEY = os.getenv('DEFAULT_STORAGE_KEY', '')  # aws or azure key
DEFAULT_STORAGE_SECRET = os.getenv('DEFAULT_STORAGE_SECRET', '')  # aws secret
DEFAULT_STORAGE_TOKEN = os.getenv('DEFAULT_STORAGE_TOKEN', '')  # aws session token
# for google storage use credentials instead of key and secret
DEFAULT_STORAGE_CREDENTIALS = os.getenv('DEFAULT_STORAGE_CREDENTIALS', '{}')
DEFAULT_STORAGE_TREAT_AS_SOURCE = (
    os.getenv('DEFAULT_STORAGE_TREAT_AS_SOURCE', 'yes') == 'yes'
)  # for all
DEFAULT_STORAGE_REGION = os.getenv('DEFAULT_STORAGE_REGION', None)  # aws
DEFAULT_STORAGE_ENDPOINT = os.getenv('DEFAULT_STORAGE_ENDPOINT', None)  # aws
DEFAULT_STORAGE_PRESIGN = (
    os.getenv('DEFAULT_STORAGE_PRESIGN', 'yes') == 'yes'
)  # for all


class Migration:
    def __init__(self, src_url, src_key, dst_url, dst_key, dest_workspace):
        """Initialize migration that copy projects from one LS instance to another

        :param src_url: source Label Studio instance
        :param src_key: source Label Studio token
        :param dst_url: destination Label Studio instance
        :param dst_key: destination Label Studio token
        :param dest_workspace: destination workspace id
        """
        # Connect to the Label Studio API and check the connection
        self.src_ls = Client(url=src_url, api_key=src_key)
        self.dst_ls = Client(url=dst_url, api_key=dst_key)
        self.users = self.projects = self.project_ids = None
        self.dest_workspace = dest_workspace

    def set_project_ids(self, project_ids=None):
        """Set projects you need to migrate

        :param project_ids: List of project ids to copy, set None if you need to copy all projects
        """
        self.project_ids = project_ids

    @staticmethod
    def add_default_import_storage(project):
        if DEFAULT_STORAGE == 's3':
            storage = project.connect_s3_import_storage(
                bucket=DEFAULT_STORAGE_BUCKET,
                regex_filter=DEFAULT_STORAGE_REGEX,
                prefix=DEFAULT_STORAGE_PREFIX,
                use_blob_urls=DEFAULT_STORAGE_TREAT_AS_SOURCE,
                aws_access_key_id=DEFAULT_STORAGE_KEY,
                aws_secret_access_key=DEFAULT_STORAGE_SECRET,
                aws_session_token=DEFAULT_STORAGE_TOKEN,
                region_name=DEFAULT_STORAGE_REGION,
                s3_endpoint=DEFAULT_STORAGE_ENDPOINT,
                presign=DEFAULT_STORAGE_PRESIGN,
                presign_ttl=15,
                title='S3 storage',
                description='migration',
            )
            logger.debug('GCS storage was connected')

        elif DEFAULT_STORAGE == 'gcs':
            storage = project.connect_google_import_storage(
                bucket=DEFAULT_STORAGE_BUCKET,
                regex_filter=DEFAULT_STORAGE_REGEX,
                prefix=DEFAULT_STORAGE_PREFIX,
                use_blob_urls=DEFAULT_STORAGE_TREAT_AS_SOURCE,
                google_application_credentials=DEFAULT_STORAGE_CREDENTIALS,
                presign=DEFAULT_STORAGE_PRESIGN,
                presign_ttl=15,
                title='GCS storage',
                description='migration',
            )
            logger.debug('Azure storage was connected')

        elif DEFAULT_STORAGE == 'azure':
            storage = project.connect_azure_import_storage(
                container=DEFAULT_STORAGE_BUCKET,
                regex_filter=DEFAULT_STORAGE_REGEX,
                prefix=DEFAULT_STORAGE_PREFIX,
                use_blob_urls=DEFAULT_STORAGE_TREAT_AS_SOURCE,
                account_name=DEFAULT_STORAGE_NAME,
                account_key=DEFAULT_STORAGE_KEY,
                presign=DEFAULT_STORAGE_PRESIGN,
                presign_ttl=1,
                title='Azure storage',
                description='migration',
            )
            logger.debug('Azure storage was connected')

        else:
            storage = None
            logger.debug('No import storage to connect')

        if storage:
            storage_type = DEFAULT_STORAGE
            project.sync_storage(storage_type, storage['id'])

            # if you need to remove duplicated tasks from your project,
            # you have to call an experimental DM action 'remove_duplicates' in this place
            # when storage sync is finished. It may look like this:
            """
            completed = False
            while not completed:
                status = project.make_request('get', f'/api/storages/s3/{storage["id"]}').json()['status']
                completed = status == 'completed'
                if status == 'failed':
                    logger.error(f'Sync failed for storage {storage}')
                    break
            if completed:
                project.make_request('post', f'api/actions?project={project.id}&id=remove_duplicates')
            """

    def run(self, project_ids=None):
        projects = self.get_projects(project_ids)
        users = self.get_users()  # self.get_users(projects)
        self.create_users(users)

        # start exporting projects
        success = 0
        for project in projects:
            success += self.migrate_project(project)

        logger.info(
            f"Projects are processed, finishing with {success} successful and {len(projects)} total projects"
        )

    def migrate_project(self, project):
        filenames = self.export_chunked_snapshots(project)
        if not filenames:
            logger.error(
                f"No exported files found: skipping project {project.id}. Maybe project is empty?"
            )
            return False

        logger.info(f"Patching snapshot users for project {project.id}")
        for filename in filenames:
            self.patch_snapshot_users(filename)

        logger.info(f"New project creation for project {project.id}")
        label_config = str(project.label_config)
        project.params["label_config"] = '<View></View>'
        new_project = self.create_project(project)

        logger.info(f"Going to import {filenames} to project {new_project.id}")
        for filename in filenames:
            new_project.import_tasks(filename)
            logger.info(f"Import {filename} finished for project {new_project.id}")
            time.sleep(1)

        new_project.set_params(label_config=label_config)
        self.add_default_import_storage(new_project)
        return True

    def create_project(self, project):
        if self.dest_workspace is not None:
            project.params["workspace"] = self.dest_workspace
        else:
            project.params.pop("workspace", None)

        logger.info(
            f'Going to create a new project "{project.params["title"]}" from old project {project.id}'
        )
        copied_fields = {
            "title",
            "description",
            "label_config",
            "expert_instruction",
            "show_instruction",
            "show_skip_button",
            "enable_empty_annotation",
            "show_annotation_history",
            "color",
            "maximum_annotations",
            "is_published",
            "model_version",
            "is_draft",
            "min_annotations_to_start_training",
            "start_training_on_annotation_update",
            "show_collab_predictions",
            "sampling",
            "show_ground_truth_first",
            "show_overlap_first",
            "overlap_cohort_percentage",
            "task_data_login",
            "task_data_password",
            "control_weights",
            "parsed_label_config",
            "evaluate_predictions_automatically",
            "config_has_control_tags",
            "skip_queue",
            "reveal_preannotations_interactively",
            "require_comment_on_skip",
            "workspace",
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
        path = "project_mapping.json"
        if os.path.exists(path):
            with open(path, "r") as f:
                mapping = json.load(f)

        mapping[old_project.id] = new_project.id

        with open(path, "w") as f:
            json.dump(mapping, f)
        logger.info(f"{path} is updated")
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

    def get_users(self, projects=None) -> [User]:
        """Get users that are members of all projects at the source instance"""
        # enterprise instance
        if self.src_ls.is_enterprise and projects:
            users = {}
            for project in projects:
                members = project.get_members()
                id_members = {member.id: member for member in members}
                logger.info(f"Get {len(members)} users from project {project.id}")
                users.update(id_members)

            self.users = list(users.values())

        # community instance doesn't have per-project members, all users have access to all projects
        else:
            self.users = self.src_ls.get_users()

        return self.users

    def create_users(self, users: [User]):
        logger.info(
            f"Going to create {len(users)} users on {self.dst_ls}. "
            f"It is normal to see errors here if a user already exists."
        )
        new_users = []
        for user in users:
            new_user = self.dst_ls.create_user(user)
            if new_user is not None:
                new_users.append(new_user)
                logger.info(f"User {new_user.email} created")
        logger.info(f"{len(new_users)} users created, total {len(users)} users")
        logger.info(f"Created users: {[u.email for u in new_users]}")
        return new_users

    def export_chunked_snapshots(self, project):
        """Export all tasks from the project in chunks and return filenames for each chunk"""

        logger.info(f'Creating chunked snapshots for project {project.id}')
        file_size, filenames, chunk_i = 100, [], 0

        while file_size > 2:  # 2 bytes is an empty json file
            start_id = CHUNK_SIZE * chunk_i
            end_id = CHUNK_SIZE * (chunk_i + 1)
            logger.info(
                f"Exporting chunk {chunk_i} from {start_id} to {end_id} tasks for project {project.id}"
            )

            # create a filters for inner ID range to split tasks into chunks
            filters = self.inner_id_range_filter(start_id, end_id)

            # create new export and save to disk
            output_dir = "snapshots"
            result = project.export(
                filters=filters,
                title=f"Migration snapshot for chunk {chunk_i}",
                serialization_options_drafts=False,
                serialization_options_annotations__completed_by=False,
                serialization_options_predictions=False,
                output_dir=output_dir,
            )
            status, filename = result["status"], result["filename"]
            if status != 200:
                logger.info(
                    f"Error while exporting chunk {chunk_i}: {status}, skipping export"
                )
                return []

            chunk_i += 1
            filename = os.path.join(output_dir, filename)
            file_size = os.path.getsize(filename)
            if file_size > 2:
                filenames.append(filename)

        return filenames

    def inner_id_range_filter(self, start_id, end_id):
        filters = Filters.create(
            Filters.AND,
            [
                Filters.item(
                    Column.inner_id,
                    Operator.GREATER_OR_EQUAL,
                    Type.Number,
                    Filters.value(start_id),
                ),
                Filters.item(
                    Column.inner_id,
                    Operator.LESS,
                    Type.Number,
                    Filters.value(end_id),
                ),
            ],
        )
        return filters

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

        with open(filename, "r", encoding="utf8") as f:
            tasks = json.load(f)

        for task in tasks:
            for annotation in task["annotations"]:
                user = annotation["completed_by"]
                if isinstance(user, int):
                    annotation["completed_by"] = {
                        "id": user,
                        "email": id_users[user].email,
                    }
                else:
                    return  # completed_by is not int, exiting

        with open(filename, "w") as out:
            json.dump(tasks, out)

        logger.info(f"Completed_by patch is applied to {filename}")


def run():
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description="Label Studio Project Migration Script"
    )
    parser.add_argument(
        "--src-url",
        dest="src_url",
        type=str,
        default="",
        help="Source Label Studio instance",
    )
    parser.add_argument(
        "--src-key",
        dest="src_key",
        type=str,
        default="",
        help="Source Label Studio token, it should be owner or administrator token",
    )
    parser.add_argument(
        "--dst-url",
        dest="dst_url",
        type=str,
        default="",
        help="Destination Label Studio instance",
    )
    parser.add_argument(
        "--dst-key",
        dest="dst_key",
        type=str,
        default="",
        help="Destination Label Studio token, it should be owner or administrator token",
    )
    parser.add_argument(
        "--project-ids",
        dest="project_ids",
        type=str,
        default=None,
        help="Project ids separated by comma, e.g.: 54,78,98",
    )
    parser.add_argument(
        "--dest-workspace",
        dest="dest_workspace",
        type=str,
        default=None,
        help="Workspace where to store projects, e.g.: 42",
    )
    args = parser.parse_args(sys.argv[1:])

    migration = Migration(
        src_url=args.src_url,
        src_key=args.src_key,
        dst_url=args.dst_url,
        dst_key=args.dst_key,
        dest_workspace=args.dest_workspace,
    )

    project_ids = (
        [int(i) for i in args.project_ids.split(",")] if args.project_ids else None
    )
    migration.run(project_ids)


if __name__ == "__main__":
    run()
