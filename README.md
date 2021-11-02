# Label Studio Enterprise Python SDK

Use this Python SDK to integrate Label Studio Enterprise into your data science and machine learning pipelines to make data labeling simpler. 

With the Label Studio Python SDK, you can perform the following tasks in a Python script:
- Create a Label Studio project, including setting up a labeling configuration. 
- Import tasks from external or local storage, including pre-annotated tasks.
- Modify project settings, such as task sampling or the model version used to display predictions. 
- Create annotations from predictions or pre-annotated tasks. 
- Retrieve task annotations, including specific subsets of tasks.  
See the [Label Studio SDK Tutorial](https://labelstud.io/guide/sdk.html) for example code snippets and additional details. 

If you want to take action not supported natively by the SDK, you can [call the API](https://labelstud.io/api) directly and consider contributing to the SDK.

## About the SDK

This is the first release of the Label Studio SDK. It supports Label Studio Enterprise, Label Studio Teams, and Label Studio Community.

- **Find a bug?** Create a GitHub issue!
- **Have a question?** [Join the Slack Community](http://slack.labelstud.io.s3-website-us-east-1.amazonaws.com/?source=github-sdk)!

## Start using the SDK

To start using the SDK in your machine learning and data science projects and pipelines, do the following:
1. Clone this repository.
2. Import the label_studio_sdk in your Python script. 

## Available classes and methods

The Label Studio SDK includes a Client class to handle authentication, a Project class to take actions related to Label Studio labeling projects, and a utils class to work with the labeling configuration. 

For all the details, see the [reference documentation](https://labelstud.io/label-studio-sdk) or [review the code directly](https://github.com/heartexlabs/label-studio-sdk/tree/master/label_studio_sdk). 

## Active learning example

If you want to write a Python script to set up an active learning workflow for labeling and training, review this [working active learning example as a Jupyter notebook](https://github.com/heartexlabs/label-studio-sdk/blob/master/examples/Active%20Learning.ipynb) or start with the [active learning python script example](https://github.com/heartexlabs/label-studio-sdk/blob/master/examples/active_learning.py).

## Weak supervision example

If you want to write a Python script to perform programmatic labeling and use weak supervision to correct the noisy labels, refer to this [working weak supervision example as a Jupyter notebook](https://github.com/heartexlabs/label-studio-sdk/blob/master/examples/Weak%20Supervision.ipynb) or start with the [weak supervision python script example](https://github.com/heartexlabs/label-studio-sdk/blob/master/examples/weak_supervision.py).