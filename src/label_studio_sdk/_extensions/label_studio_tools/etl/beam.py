import apache_beam as beam
from registry import dataloader, call_dataloader


class CallDataLoader(beam.DoFn):
    def __init__(self, dataloader_name):
        self.dataloader_name = dataloader_name

    def setup(self):
        print("Setup!")
        pass

    def process(self, element, *args, **kwargs):
        return call_dataloader(self.dataloader_name, element, *args, **kwargs)

    def teardown(self):
        print("Teardown!")
        pass


@dataloader("test")
def f(i, k):
    print("I!!", k)
    yield i


with beam.Pipeline() as pipeline:
    results = (
        pipeline
        | "Get storage keys" >> beam.io.gcp.gcsio.list_files("bucket")
        | "Run dataloader"
        >> beam.FlatMap(fn=CallDataLoader("test"), **dataloader_kwargs)
        | "Load into Vector DB" >> beam.ParDo(fn=LoadDataRecordInDB)
    )
