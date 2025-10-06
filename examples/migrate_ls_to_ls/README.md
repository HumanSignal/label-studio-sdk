# Migrate from one Label Studio instance to another 

This migration helps to copy projects from one LS instance to another. To be copied:
* Users
* Projects
* Tasks
* Annotations
* Predictions
* Reviews (you should request our team to enable it on SaaS side for your organization)
* Drafts (you should request our team to enable it on SaaS side for your organization)

Not supported:
* Cloud Storages are not supported.
* Files and media uploaded using UI imports are not supported and won't be copied. 
* Other entities are not supported. 

Each new run of this script will generate new projects on the destination instance.

# Prerequisites

**Attention:** You must use Administrator or better Owner auth token on both LSE instances to run this script. 

**Note:** Create a new workspace and get its ID for projects to be mgiratated. 

**SDK v2.0 or higher**

```
pip install -U label-studio-sdk
```

# How it works? 

1. Get all projects from source LS (or specific projects)
2. Get all users from the organization
3. Create all users with the same emails, first names and last names on the target LS instance 
4. For each project:

    4.1. export on the source LS instance, wait until export is done
    > Note: if there is an export error, skip this project
    
    4.2. create a new project on the target LS instance with the same params as on source instance, except review settings and assignment settings (enterprise only) 
    > Note: Cloud storages, ML backends, Members, Webhooks are not copied. Data manager tabs and other advanced things are not copied too
 
    4.3. import **tasks**, **annotations** and **predictions** from the exported file
 
    4.4. write old project id => new project id mapping to `project_mapping.json` in the directory where you run the migration script.  

# Usage

1. Install Label Studio SDK:

    ```
    pip install -U label-studio-sdk
    ```

2. Go to source (src) and destination (dst) LS instances. Open Account pages (/user/account), copy your Access tokens. 

    > **Attention**: Be careful not to mix up the tokens, otherwise there is a chance you will create a big mess of projects and users.

    > Note: User token must have Administrator or Owner privileges.

3. Migrate projects from the organization:

    It's highly recommended to start with **one project only**, to achieve this use the `--project-ids` option:

    ```
    python3 migrate-ls-to-ls.py --project-ids=123,456 \
        --src-url http://localhost:8000 --src-key <src-token> \
        --dst-url https://app.humansignal.com --dst-key <dst-token>
    ```

    To migrate all projects:

    ```
    python3 migrate-ls-to-ls.py \
        --src-url http://localhost:8000 --src-key <src-token> \
        --dst-url https://app.humansignal.com --dst-key <dst-token>
    ```

5. Migrate all projects to the specific workspace (optional)

   It's recommended to create a new workspace on the destination machine and migrate projects there.


    ```
    python3 migrate-ls-to-ls.py --project-ids=123,456 \ 
        --src-url http://localhost:8000 --src-key <src-token> \ 
        --dst-url https://app.humansignal.com --dst-key <dst-token> \
        --dest-workspace <workspace-id>
    ```


     To know workspace ID you should open a network console, select a newly created workspace or refresh the page fully, and find `/api/workspaces/**<id>**/memberships` call in the network console. 
