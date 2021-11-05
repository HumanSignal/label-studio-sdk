""" Data manager classes help to operate with filtering, ordering and selected items in `label_studio_sdk.project.Project.get_tasks`
    and provides enumeration for all column names in the task available in the Data Manager and other helpers.

    Example:

    ```python
    Filters.create(Filters.OR, [
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
    ```
"""
from datetime import datetime

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'


class Filters:
    OR = 'or'
    AND = 'and'

    @staticmethod
    def create(conjunction, items):
        """ Create filters parameter for `label_studio_sdk.project.Project.get_tasks()`

        Parameters
        ----------
        conjunction
        items

        Returns
        -------

        """
        return {
          "conjunction": conjunction,
          "items": items
        }

    @staticmethod
    def item(name, operator, column_type, value):
        return {
            "filter": name,
            "operator": operator,
            "type": column_type,
            "value": value
        }

    @staticmethod
    def datetime(dt):
        """ Date time string format for filters
        Parameters
        ----------
        dt
            datetime instance

        Returns
        -------
        str
           datetime in '%Y-%m-%dT%H:%M:%S.%fZ' format

        """
        assert isinstance(dt, datetime), 'dt must be datetime type'
        return dt.strftime(DATETIME_FORMAT)

    @classmethod
    def value(cls, value, maximum=None):
        """

        Parameters
        ----------
        value: str | int | float | datetime | boolean
            value for filtering, if maximum is passed then value is minimum

        maximum: int | float  | datetime
            Range for IN, NOT_IN operators

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
    Number = 'Number'
    Datetime = 'Datetime'
    Boolean = 'Boolean'
    String = 'String'
    List = "List"

    Unknown = 'Unknown'
    """ Unknown will be explicitly converter to String """


class Column:

    # TODO: @sarah some of these fields are enterprise only, please mark them somehow;
    #  also we need desc for the each enumeration

    id = "filter:tasks:id"
    ground_truth = "filter:tasks:ground_truth"
    annotations_results = "filter:tasks:annotations_results"
    reviewed = "filter:tasks:reviewed"
    predictions_score = "filter:tasks:predictions_score"
    predictions_model_versions = "filter:tasks:predictions_model_versions"
    predictions_results = "filter:tasks:predictions_results"
    file_upload = "filter:tasks:file_upload"
    created_at = "filter:tasks:created_at"
    annotators = "filter:tasks:annotators"
    total_predictions = "filter:tasks:total_predictions"
    cancelled_annotations = "filter: tasks:cancelled_annotations"
    total_annotations = "filter:tasks:total_annotations"
    completed_at = "filter:tasks:completed_at"
    agreement = "filter:tasks:agreement"
    reviewers = "filter:tasks:reviewers"
    reviews_rejected = "filter:tasks:reviews_rejected"
    reviews_accepted = "filter:tasks:reviews_accepted"

    @staticmethod
    def data(task_field):
        """ Generate filter name for task data field

        Parameters
        ----------
        task_field

        Returns
        -------
        str
            Filter name for task data

        """
        return "filter:tasks:data." + task_field


def test():
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
