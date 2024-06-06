import logging

from functools import wraps
from typing import Callable, Iterable, Dict, Any

logger = logging.getLogger(__name__)


class extract:
    pass


class transform:
    DataRecords = Iterable[Dict[str, Any]]
    DataRecordsProducer = Callable[..., DataRecords]

    class NameAlreadyExists(KeyError):
        pass

    class NameNotFound(NotImplementedError):
        pass

    class WrongOutput(ValueError):
        pass

    registry = {}

    @staticmethod
    def datarecords(name: str = None):
        """Class method to register transform function to produce DataRecords
        with specified name to the internal registry.
        Can output any iterable for dicts (generators, iterators, list, tuples)
        For example:

        @transform.datarecords("DataRecords from GCS file")
        def read_image(bucket_name, key):
            yield {"image": blob.download_as_string()}
        """

        def register_transform_func(
            transform_func: transform.DataRecordsProducer,
        ) -> transform.DataRecordsProducer:
            if name in transform.registry:
                raise transform.NameAlreadyExists(
                    f"Dataloader {name} already exists. Will replace it"
                )
            transform.registry[name] = transform_func

            @wraps(transform_func)
            def inner_call_transform_func(*args, **kwargs) -> transform.DataRecords:
                data_records = transform_func(*args, **kwargs)
                # TODO: assert Data record type in a proper way, typing.assert_type is supported in Python 3.11
                return data_records

            return inner_call_transform_func

        return register_transform_func

    @staticmethod
    def invoke(name, *args, **kwargs):
        if name not in transform.registry:
            raise transform.NameNotFound(name)
        return transform.registry[name](*args, **kwargs)


class load:
    pass
