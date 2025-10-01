""" This script runs every 10 seconds and assigns users to a new batch of tasks filtered by the specified column.

Advanced notes:
    1. Don't forget to enable Manual mode in Annotation settings
    2. Be careful when adding email users: users who are not members of the project or workspace will break Data Manager

Install:
    git clone https://github.com/heartexlabs/label-studio-sdk.git
    cd label-studio-sdk
    pip install -e .
    python examples/label_studio_enterprise/assigner.py

Demo video:
    https://www.youtube.com/watch?v=IeqrsCYYQ8k
"""

import math
import time

import os
from label_studio_sdk import LabelStudio
from label_studio_sdk.data_manager import Filters, Column, Operator, Type


class BatchAssigner:
    def __init__(self, host, api_key, project_id):
        self.ls = LabelStudio(base_url=host, api_key=api_key)
        self.project = self.ls.projects.get(id=project_id)

    def get_tasks(self, filter_column, filter_value, page, page_size):
        """Get tasks with filter by column and page number"""
        filters = Filters.create(
            Filters.OR,
            [
                Filters.item(
                    Column.data(filter_column),
                    Operator.EQUAL,
                    Type.String,
                    Filters.value(filter_value),
                )
            ],
        )
        return self.ls.tasks.list(project=self.project.id, query=filters, fields='id', page_size=page_size, page=page)

    def get_page_total(self, filter_column, filter_value, page_size):
        """Total page number for tasks with filter by column and specified page size"""
        result = self.get_tasks(filter_column, filter_value, 1, page_size)
        breakpoint()
        return math.ceil(result.total / float(page_size))

    def get_user_ids(self, emails):
        """Get user IDs by email and preserve the order

        :param emails: list of strings with email addresses
        :return: user IDs in the same order as email addresses
        """
        # get all users
        user_ids = []
        users = self.ls.users.list()
        for email in emails:
            for user in users:
                if email == user.email:
                    print(user.email, "=>", user.id)
                    user_ids.append(user.id)
                    break

        return user_ids

    def assign_users_to_tasks(
        self,
        user_ids,
        filter_column="organization",
        filter_value="name",
        page=1,
        page_size=100,
    ):
        """Assign annotators to filter by specified column and paginated tasks

        :param user_ids: list of user email addresses
        :param filter_column: str with data column name from Data Manager
        :param filter_value: str with data value to filter as equal
        :param page: current page
        :param page_size: task number
        :return: True if success else False or exception
        """

        result = self.get_tasks(filter_column, filter_value, page, page_size)
        task_ids = result["tasks"]

        if not task_ids:
            print(f"No tasks found")
            return False

        # call assign API
        body = {
            "type": "AN",
            "users": user_ids,
            "selectedItems": {"all": False, "included": task_ids},
        }
        self.ls.make_request("post", f"/api/projects/{self.project.id}/tasks/assignees", json=body)
        print(
            f"Users {user_ids} were assigned to {len(task_ids)} tasks "
            f"from id={task_ids[0]} to id={task_ids[-1]}"
        )
        return True


def start():
    host = os.getenv("LABEL_STUDIO_URL", "http://localhost:8080")
    api_key = os.getenv("LABEL_STUDIO_API_KEY", "")
    project_id = int(os.getenv("LABEL_STUDIO_PROJECT_ID", "182"))

    filter_column = "shortname"
    filter_value = "opossum"
    page_size = 10
    emails = os.getenv("LABEL_STUDIO_ASSIGN_EMAILS", "user1@example.com,user2@example.com").split(",")

    assigner = BatchAssigner(host, api_key, project_id)

    # Be careful when using email users:
    # users who are not members of the project or workspace will break Data Manager
    user_ids = assigner.get_user_ids(emails=emails)

    page_total = assigner.get_page_total(filter_column, filter_value, page_size)
    print(f"Total pages for {filter_column}={filter_value} => {page_total}")

    for current_page in range(1, page_total + 1):
        assigner.assign_users_to_tasks(
            filter_column=filter_column,
            filter_value=filter_value,
            user_ids=user_ids,
            page=current_page,
            page_size=page_size,
        )

        time.sleep(10)


if __name__ == "__main__":
    start()
