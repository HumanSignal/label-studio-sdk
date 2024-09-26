"""
This script is meant to automatically tag tasks within a project using a random distribution and
then assign those that receive a specific tag to a reviewer for further reviewing.

**Note:** This code utilizes functions from an older version of the Label Studio SDK (v0.0.34).
While the newer versions v1.0 and above still support the functionalities of the old version
(see `label_studio_sdk._legacy` for reference), we recommend using the latest Label Studio SDK v1.0 or higher.
"""

from label_studio_sdk import Client
from label_studio_sdk.data_manager import Filters, Column, Operator, Type

# Initialize the Label Studio SDK Client
LABEL_STUDIO_URL = "https://app.heartex.com"  # Replace with your Label Studio URL
API_KEY = "<ls-api-key>"  # Replace with your API key
ls = Client(url=LABEL_STUDIO_URL, api_key=API_KEY)


def create_tags_with_random_distribution(
    project_id: int, column_name: str, choices: list, weights: list
):
    """Generate a new task column with tags randomly distributed by weights (percents).
    For example, if column_name='tags', choices=['to-be-reviewed', 'others'] and weights=[0.1, 0.9],
    10% of tasks will have 'to-be-reviewed' in newly created 'tags' column.

    Note: this API call uses experimental feature, use this with caution because you can overwrite
    your task columns with this command.

    :param project_id: project id
    :param column_name: string, a new column name to be created
    :param choices: array of strings, tag names
    :param weights: sampling for tag names, values should be from 0.0 to 10 and sum(weights) should be 1.0
    :return: API response for sampling
    """

    assert len(choices) == len(weights)
    data = {
        "ordering": [],
        "selectedItems": {"all": True, "excluded": []},
        "filters": {"conjunction": "and", "items": []},
        "value_name": column_name,
        "value_type": "Expression",
        "value": f"choices({choices}, {weights})",
        "project": project_id,
    }
    response = ls.make_request(
        "post", f"/api/dm/actions?id=add_data_field&project={project_id}", json=data
    )
    print("Tag sampling is done")
    return response


def assign_reviewer_by_tag(
    project_id: int, reviewer_email: str, filter_column: str, filter_value: str
):
    """Function to assign a reviewer to tasks filtered by a specific tag

    :param project_id: project id
    :param reviewer_email: user email to be a reviewer
    :param filter_column: column name to use in the filter
    :param filter_value: value name to use in the filter
    :return: API response for the reviewer assignment
    """
    # Get the user ID of the reviewer by their email
    users = ls.get_users()
    reviewer = next((user for user in users if user.email == reviewer_email), None)
    if not reviewer:
        raise ValueError(f"Reviewer with email {reviewer_email} not found.")

    # Create a filter for tasks with the specified tag
    filters = Filters.create(
        Filters.AND,
        [
            Filters.item(
                Column.data(filter_column),
                Operator.EQUAL,
                Type.String,
                Filters.value(filter_value),
            )
        ],
    )

    # Retrieve the filtered tasks
    project = ls.get_project(project_id)
    task_ids = project.get_tasks_ids(filters=filters)

    # Assign the reviewer to the filtered tasks
    response = project.assign_reviewers([reviewer], task_ids)
    print(f"Assigned reviewer {reviewer_email} to {len(task_ids)} tasks")
    return response


def run():
    """This function acts as the main entry point for running the defined operations.

    It specifies the project ID and reviewer's email, and then:
    1. Calls create_tags_with_random_distribution to add a 'tags' column to the project's tasks
     with tags 'to-be-reviewed' or 'other', distributed according to the specified weights
    2. Calls assign_reviewer_by_tag to assign the specified reviewer to all tasks
     that have been tagged as 'to-be-reviewed'.
    """
    project_id = 12716  # Replace with your actual project ID
    reviewer_email = "your@email.com"  # Replace with the reviewer's email

    create_tags_with_random_distribution(
        project_id, "tags", choices=["to-be-reviewed", "other"], weights=[0.1, 0.9]
    )
    assign_reviewer_by_tag(
        project_id, reviewer_email, filter_column="tags", filter_value="to-be-reviewed"
    )


if __name__ == "__main__":
    run()
