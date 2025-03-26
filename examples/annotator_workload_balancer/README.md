# Annotator Workload Balancer

This example demonstrates how to use the Label Studio SDK to automatically detect and rebalance workload differences between annotators in a Label Studio project.

## Overview

The script monitors the distribution of pending annotation tasks among annotators and automatically reassigns tasks when the workload becomes imbalanced. This helps maintain an even distribution of work, prevents annotator overload, and ensures more consistent project completion timelines.

## Features

- Periodically checks annotator workloads
- Identifies overloaded and underloaded annotators
- Automatically reassigns tasks when imbalance exceeds a configurable threshold
- Detailed logging of workload status and rebalancing operations
- Configurable check intervals and rebalance thresholds

## Requirements

- Python 3.7+
- Label Studio SDK

## Installation

```bash
pip install label-studio-sdk
```

## Usage

1. Configure the script with your Label Studio URL, API key, and project ID
2. Set the rebalance threshold and check interval as needed
3. Run the script:

```bash
python rebalance_annotator_workload.py
```

## Configuration

```python
# Configuration - Replace these with your actual details
LABEL_STUDIO_URL = "https://app.heartex.com"  # Your Label Studio URL
API_KEY = "your_api_key_here"  # Your API key
PROJECT_ID = 0  # Your project ID
REBALANCE_THRESHOLD = 2  # Trigger rebalance when difference > this value
CHECK_INTERVAL = 30  # Time between checks (in seconds)
```

## How It Works

1. The script connects to your Label Studio instance using the SDK
2. It retrieves all tasks and analyzes their assignment and completion status
3. It calculates the pending workload for each annotator
4. If the difference between the most and least loaded annotators exceeds the threshold, it:
   - Identifies a pending task from the overloaded annotator
   - Reassigns it to the underloaded annotator

## Example Output

```
Starting Label Studio workload balancer
Project ID: 123
Rebalance threshold: 2 tasks
Check interval: 30 seconds
Press Ctrl+C to stop

==================================================
Checking for workload imbalance at 2023-09-15 14:30:45
==================================================
Retrieved 100 tasks from project 123

--- ASSIGNMENT SUMMARY ---
Annotator workloads (sorted by pending tasks):
  Annotator 456: 40 total, 32 pending, 8 completed
  Annotator 789: 35 total, 20 pending, 15 completed
  Annotator 123: 40 total, 18 pending, 22 completed
------------------------

Most loaded annotator: 456 with 32 pending tasks
Least loaded annotator: 123 with 18 pending tasks
Difference: 14 tasks
Workload imbalance detected (difference > 2). Rebalancing...
Successfully reassigned task 78901 from annotator 456 to 123
Next check in 30 seconds...
```