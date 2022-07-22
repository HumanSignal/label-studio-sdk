""" # Data Manager module for the Label Studio SDK

    Classes can be used to filter, order, and select items in `label_studio_sdk.project.Project.get_tasks`
    and provides enumeration for all column names available in the Data Manager for tasks, and other helpers.

    See the [client](client.html), [project](project.html) or [utils](utils.html) modules for other operations you
    might want to perform.

    Example:

    ```python
    from label_studio_sdk.data_manager import Filters, Column, Operator, Type

    filters = Filters.create(Filters.OR, [
        Filters.item(
            Column.id,
            Operator.GREATER,
            Type.Number,
            Filters.value(42)
        ),
        Filters.item(
            Column.completed_at,
            Operator.IN,
            Type.Datetime,
            Filters.value(
                datetime(2021, 11, 1),
                datetime.now()
            )
        )
    ])
    tasks = project.get_tasks(filters=filters)
    ```
"""
from datetime import datetime

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'


class Filters:
    """
    Use the methods and variables in this class to create and combine filters for tasks on the Label Studio Data Manager.
    """
    OR = 'or'
    """Combine filters with an OR"""
    AND = 'and'
    """Combine filters with an AND"""

    @staticmethod
    def create(conjunction, items):
        """ Create a filter for `label_studio_sdk.project.Project.get_tasks()`

        Parameters
        ----------
        conjunction: str
            The conjunction operator between filters ('or' or 'and')
        items: list
            What to filter, use `Filter.item()` method to build it

        Returns
        -------
        dict
            containing specified parameters

        """
        return {
          "conjunction": conjunction,
          "items": items
        }

    @staticmethod
    def item(name, operator, column_type, value):
        """Use in combination with other classes to specify the contents of a filter.

        Parameters
        ----------
        name: `Column` or str
            Column.id, Column.completed_at, Column.data('my_field'), etc
        operator: `Operator`
            Operator.EQUAL, Operator.GREATER_OR_EQUAL, Operator.IN, etc
        column_type: `Type`
            Type.Number, Type.Boolean, Type.String, etc
        value: `Filters.value()`
            Filters.value(42), Filters.value('test'), Filters.value(datetime(2021, 01, 01), datetime.now())

        Returns
        -------
        dict
        """
        return {
            "filter": 'filter:' + name,
            "operator": operator,
            "type": column_type,
            "value": value
        }

    @staticmethod
    def datetime(dt):
        """ Date time string format for filtering the Data Manager.

        Parameters
        ----------
        dt
            datetime instance

        Returns
        -------
        str
            datetime in `'%Y-%m-%dT%H:%M:%S.%fZ'` format

        """
        assert isinstance(dt, datetime), 'dt must be datetime type'
        return dt.strftime(DATETIME_FORMAT)

    @classmethod
    def value(cls, value, maximum=None):
        """Set a filter value in the Data Manager.

        Parameters
        ----------
        value: str | int | float | datetime | boolean
            value to use for filtering. If the maximum parameter is passed, then this value field is the minimum.

        maximum: int | float  | datetime
            Specify a maximum for a filtering range with IN, NOT_IN operators.

        Returns
        -------
        any
            value for filtering

        """
        if isinstance(value, datetime):
            value = cls.datetime(value)

        if maximum is not None:
            if isinstance(maximum, datetime):
                maximum = cls.datetime(maximum)
            return {'min': value, 'max': maximum}

        return value


class Operator:
    """Specify the operator to use when creating a filter.
    """

    EQUAL = "equal"
    NOT_EQUAL = "not_equal"
    LESS = "less"
    GREATER = "greater"
    LESS_OR_EQUAL = "less_or_equal"
    GREATER_OR_EQUAL = "greater_or_equal"
    IN = "in"
    NOT_IN = "not_in"
    IN_LIST = "in_list"
    NOT_IN_LIST = "not_in_list"
    EMPTY = "empty"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    REGEX = "regex"


class Type:
    """Specify the type of data in a column.
    """

    Number = 'Number'
    Datetime = 'Datetime'
    Boolean = 'Boolean'
    String = 'String'
    List = "List"

    Unknown = 'Unknown'
    """ Unknown is explicitly converted to string format. """


class Column:
    """Specify the column on the Data Manager in Label Studio UI to use in the filter.
    """

    id = "tasks:id"
    """Task ID"""
    ground_truth = "tasks:ground_truth"
    """Ground truth status of the tasks"""
    annotations_results = "tasks:annotations_results"
    """Annotation results for the tasks"""
    reviewed = "tasks:reviewed"
    """Whether the tasks have been reviewed (Enterprise only)"""
    predictions_score = "tasks:predictions_score"
    """Prediction score for the task"""
    predictions_model_versions = "tasks:predictions_model_versions"
    """Model version used for the predictions"""
    predictions_results = "tasks:predictions_results"
    """Prediction results for the tasks"""
    file_upload = "tasks:file_upload"
    """Name of the file uploaded to create the tasks"""
    created_at = "tasks:created_at"
    """Time the task was created at"""
    annotators = "tasks:annotators"
    """Annotators that completed the task (Community). Can include assigned annotators (Enterprise only)"""
    total_predictions = "tasks:total_predictions"
    """Total number of predictions for the task"""
    cancelled_annotations = "tasks:cancelled_annotations"
    """Number of cancelled or skipped annotations for the task"""
    total_annotations = "tasks:total_annotations"
    """Total number of annotations on a task"""
    completed_at = "tasks:completed_at"
    """Time when a task was fully annotated"""
    agreement = "tasks:agreement"
    """Agreement for annotation results for a specific task (Enterprise only)"""
    reviewers = "tasks:reviewers"
    """Reviewers that reviewed the task, or assigned reviewers (Enterprise only)"""
    reviews_rejected = "tasks:reviews_rejected"
    """Number of annotations rejected for a task in review (Enterprise only)"""
    reviews_accepted = "tasks:reviews_accepted"
    """Number of annotations accepted for a task in review (Enterprise only)"""

    @staticmethod
    def data(task_field):
        """ Create a filter name for the task data field

        Parameters
        ----------
        task_field

        Returns
        -------
        str
            Filter name for task data

        """
        return "tasks:data." + task_field


def _test():
    """Test it"""
    filters = Filters.create(Filters.OR, [
        Filters.item(
            Column.id,
            Operator.GREATER,
            Type.Number,
            Filters.value(42)
        ),
        Filters.item(
            Column.completed_at,
            Operator.IN,
            Type.Datetime,
            Filters.value(
                datetime(2021, 11, 1),
                datetime(2021, 11, 5),
            )
        )
    ])

    assert filters == {'conjunction': 'or',
                       'items': [
                           {'filter': 'filter:tasks:id', 'operator': 'greater', 'type': 'Number', 'value': 42},
                           {'filter': 'filter:tasks:completed_at', 'operator': 'in', 'type': 'Datetime',
                            'value': {
                                'min': '2021-11-01T00:00:00.000000Z',
                                'max': '2021-11-05T00:00:00.000000Z'}
                            }
                         ]
                       }
