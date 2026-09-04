import time
import label_studio_sdk
import json

# Configuration - Replace these with your actual details
LABEL_STUDIO_URL = "https://app.heartex.com"  # Your Label Studio URL
API_KEY = "your_api_key_here"  # Your API key
PROJECT_ID = 0  # Your project ID
REBALANCE_THRESHOLD = 2  # Trigger rebalance when difference > this value
CHECK_INTERVAL = 30  # Time between checks (in seconds)

def get_pending_task_counts(tasks):
    """
    Analyze tasks and build dictionaries of total and pending task counts per annotator.
    
    Args:
        tasks: List of task objects from Label Studio API
        
    Returns:
        Dictionary with annotator IDs as keys and pending task counts as values
    """
    # Track both total assignments and pending assignments
    total_counts = {}
    pending_counts = {}
    
    for task in tasks:
        task_id = task.get('id', 'unknown')
        
        # Identify which annotators have completed this task
        annotations = task.get('annotations', [])
        completed_by = set()
        for annotation in annotations:
            if 'completed_by' in annotation:
                # Handle different formats of completed_by (dict or string)
                if isinstance(annotation['completed_by'], dict):
                    if 'id' in annotation['completed_by']:
                        completed_by.add(str(annotation['completed_by']['id']))
                else:
                    completed_by.add(str(annotation['completed_by']))
        
        # Process each annotator assigned to this task
        annotators = task.get('annotators', [])
        for annotator in annotators:
            # Extract annotator ID from different possible structures
            if isinstance(annotator, dict):
                if 'id' in annotator:
                    annotator_id = str(annotator['id'])
                elif 'user_id' in annotator:
                    annotator_id = str(annotator['user_id'])
                else:
                    continue  # Skip if we can't identify the annotator
            else:
                annotator_id = str(annotator)
            
            # Count total assignments
            total_counts[annotator_id] = total_counts.get(annotator_id, 0) + 1
            
            # Only count pending tasks (not completed by this annotator)
            if annotator_id not in completed_by:
                pending_counts[annotator_id] = pending_counts.get(annotator_id, 0) + 1
    
    # Print summary of assignments
    print("\n--- ASSIGNMENT SUMMARY ---")
    print("Annotator workloads (sorted by pending tasks):")
    
    # Sort annotators by pending task count (highest first)
    sorted_annotators = sorted(
        total_counts.keys(), 
        key=lambda a: pending_counts.get(a, 0), 
        reverse=True
    )
    
    for annotator_id in sorted_annotators:
        total = total_counts[annotator_id]
        pending = pending_counts.get(annotator_id, 0)
        completed = total - pending
        print(f"  Annotator {annotator_id}: {total} total, {pending} pending, {completed} completed")
    
    print("------------------------\n")
    
    return pending_counts

def rebalance_assignments():
    """
    Main function to check for workload imbalance and reassign tasks if needed.
    """
    print("Fetching tasks from Label Studio...")
    
    # Connect to Label Studio
    try:
        client = label_studio_sdk.Client(url=LABEL_STUDIO_URL, api_key=API_KEY)
        project = client.get_project(PROJECT_ID)
    except Exception as e:
        print(f"Error connecting to Label Studio: {e}")
        return
    
    # Retrieve all tasks
    try:
        tasks = project.get_tasks(only_ids=False)
        if not tasks:
            print("No tasks found in the project.")
            return
        print(f"Retrieved {len(tasks)} tasks from project {PROJECT_ID}")
    except Exception as e:
        print(f"Error retrieving tasks: {e}")
        return

    # Get counts of pending tasks per annotator
    pending_counts = get_pending_task_counts(tasks)
    
    if not pending_counts:
        print("No pending tasks found.")
        return
    
    if len(pending_counts) < 2:
        print("Need at least two annotators with pending tasks to perform balancing.")
        return

    # Identify the overloaded and underloaded annotators
    overloaded = max(pending_counts, key=lambda a: pending_counts[a])
    underloaded = min(pending_counts, key=lambda a: pending_counts[a])
    max_count = pending_counts[overloaded]
    min_count = pending_counts[underloaded]

    print(f"Most loaded annotator: {overloaded} with {max_count} pending tasks")
    print(f"Least loaded annotator: {underloaded} with {min_count} pending tasks")
    print(f"Difference: {max_count - min_count} tasks")

    # Check if rebalancing is needed
    if max_count - min_count <= REBALANCE_THRESHOLD:
        print(f"Workload is balanced (difference ≤ {REBALANCE_THRESHOLD}); no reassignment needed.")
        return

    print(f"Workload imbalance detected (difference > {REBALANCE_THRESHOLD}). Rebalancing...")

    # Find a pending task to reassign
    task_to_move = find_task_to_reassign(tasks, overloaded)
    
    if not task_to_move:
        print("No suitable task found for reassignment.")
        return

    # Perform the reassignment
    try:
        reassign_task(client, task_to_move, overloaded, underloaded)
        print(f"Successfully reassigned task {task_to_move} from annotator {overloaded} to {underloaded}")
    except Exception as e:
        print(f"Error during reassignment: {e}")

def find_task_to_reassign(tasks, overloaded_annotator):
    """
    Find a pending task assigned to the overloaded annotator that can be reassigned.
    
    Args:
        tasks: List of task objects
        overloaded_annotator: ID of the annotator with too many tasks
        
    Returns:
        ID of a task that can be reassigned, or None if no suitable task is found
    """
    for task in tasks:
        # Check if this task has been completed by anyone
        annotations = task.get('annotations', [])
        completed_by = set()
        for annotation in annotations:
            if 'completed_by' in annotation:
                if isinstance(annotation['completed_by'], dict):
                    if 'id' in annotation['completed_by']:
                        completed_by.add(str(annotation['completed_by']['id']))
                else:
                    completed_by.add(str(annotation['completed_by']))
        
        # Check if the overloaded annotator is assigned to this task
        annotators = task.get("annotators", [])
        for annotator in annotators:
            annotator_id = None
            if isinstance(annotator, dict):
                annotator_id = str(annotator.get('id', '')) or str(annotator.get('user_id', ''))
            else:
                annotator_id = str(annotator)
            
            # Only consider tasks that are assigned to overloaded annotator AND not completed by them
            if annotator_id == overloaded_annotator and annotator_id not in completed_by:
                return task["id"]
    
    return None

def reassign_task(client, task_id, from_annotator, to_annotator):
    """
    Reassign a task from one annotator to another.
    
    Args:
        client: Label Studio client
        task_id: ID of the task to reassign
        from_annotator: ID of the annotator to remove
        to_annotator: ID of the annotator to add
    """
    # Get current task details
    response = client.make_request("get", f"/api/tasks/{task_id}")
    task_info = response.json()
    
    # Extract current annotators
    current_assign = task_info.get("annotators", [])
    
    # Convert to list of IDs
    current_assign_ids = []
    for annotator in current_assign:
        if isinstance(annotator, dict):
            if 'id' in annotator:
                current_assign_ids.append(str(annotator['id']))
            elif 'user_id' in annotator:
                current_assign_ids.append(str(annotator['user_id']))
        else:
            current_assign_ids.append(str(annotator))
    
    # Create new assignment list
    new_assign_ids = [a for a in current_assign_ids if a != from_annotator]
    if to_annotator not in new_assign_ids:
        new_assign_ids.append(to_annotator)

    # Prepare the payload to update this task's assignment
    body = {
        "type": "AN",  # "AN" for annotators; "RE" for reviewers
        "users": new_assign_ids,
        "selectedItems": {"all": False, "included": [task_id]},
        "filters": {"conjunction": "and", "items": []},
        "action": "set"
    }
    
    # Make the API request
    client.make_request("post", f"/api/projects/{PROJECT_ID}/tasks/assignees", json=body)

def main():
    """
    Main function to run the rebalancing script periodically.
    """
    print(f"Starting Label Studio workload balancer")
    print(f"Project ID: {PROJECT_ID}")
    print(f"Rebalance threshold: {REBALANCE_THRESHOLD} tasks")
    print(f"Check interval: {CHECK_INTERVAL} seconds")
    print("Press Ctrl+C to stop\n")
    
    while True:
        try:
            print("\n" + "="*50)
            print(f"Checking for workload imbalance at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*50)
            rebalance_assignments()
            print(f"Next check in {CHECK_INTERVAL} seconds...")
            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            print("\nStopping workload balancer")
            break
        except Exception as e:
            print(f"Error: {e}")
            print(f"Retrying in {CHECK_INTERVAL} seconds...")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()