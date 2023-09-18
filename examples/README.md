# Example scripts for Label Studio SDK

These end-to-end examples demonstrate how to use the SDK for specific use cases.

### [Active learning example](active_learning)

If you want to write a Python script to set up an active learning workflow for labeling and training, review this 
* [working active learning example as a Jupyter notebook](https://github.com/heartexlabs/label-studio-sdk/blob/master/examples/active_learning/active_learning.ipynb) or
* start with the [active learning python script example](https://github.com/heartexlabs/label-studio-sdk/blob/master/examples/active_learning/active_learning.py).

### [Annotate data from Google Cloud Storage](annotate_data_from_gcs)

If your data is hosted in Google Cloud Storage (GCS), you can write a Python script to continuously sync data from the bucket with Label Studio. Follow this example to see how to do that with the Label Studio SDK. It's convenient and secure to host data in the cloud for data labeling, then sync task references to Label Studio to allow annotators to view and label the tasks without your data leaving the secure cloud bucket, LS won't touch your bucket data directly, only user browsers will do it. 

### [Import preannotations](import_preannotations)

These scripts will help you import tasks with preannotations (predictions). 
* [import_brush_predictions.py](import_preannotations/import_brush_predictions.py) - this example shows how to import masks for BrushLabels
* [import_preannotations.py](import_preannotations/import_preannotations.py) - import tasks with preannotations for the classification labeling config

### [Label Studio Enterprise](label_studio_enterprise)

Scripts for the enterprise version of Label Studio. 

* [label_studio_enterprise/assigner.py](label_studio_enterprise/assigner.py) - This script runs every 10 seconds and assigns users to a new batch of tasks filtered by the specified column.
* [label_studio_enterprise/assignment.ipynb](label_studio_enterprise/assignment.ipynb) - This tutorial describes the basics of assigning users to projects, workspaces, and specific tasks in Label Studio Enterprise using the Python SDK.
* [label_studio_enterprise/user_management.ipynb](label_studio_enterprise/user_management.ipynb) - This tutorial describes the basics of managing users in Label Studio Enterprise using the Python SDK.

### [Migrate LS to LS](migrate_ls_to_ls)

This script does the migration from one Label Studio instance to another (enterprise versions are supported too) using API. 

### [Weak supervision example](weak_supervision)

If you want to write a Python script to perform programmatic labeling and use weak supervision to correct the noisy labels, refer to this [working weak supervision example as a Jupyter notebook](https://github.com/heartexlabs/label-studio-sdk/blob/master/examples/weak_supervision/weak_supervision.ipynb) or start with the [weak supervision python script example](https://github.com/heartexlabs/label-studio-sdk/blob/master/examples/weak_supervision/weak_supervision.py).

### Others
* [Adding new labels to the project](adding_new_labels_to_project.ipynb) - This tutorial demonstrates how to add new labels to an ongoing project in real-time. The included example showcases the use of the <Taxonomy> tag, which can be applied to the entire document. However, this same principle can also be used for other cases, such as modifying labels for computer vision applications (bounding boxes, polygons, etc.), or segments in text and audio using nested <Taxonomy> tags.
* [Export snapshots](export_snapshots.py) - This example shows how to export, check export status and download JSON shapshots from Label Studio.
* [Data Manager tab management](view_management.ipynb) - This tutorial describes the basics of managing views (tabs) in Label Studio Data Manager using the Python SDK.

<img src="https://labelstud.io/images/opossum/other/5.svg" width="400px">
