# pip install -U label-studio-sdk
from label_studio_sdk.client import LabelStudio

# Authentication parameters:
# # https://api.labelstud.io/api-reference/introduction/getting-started#authentication
BASE_URL = "https://app.humansignal.com"
API_KEY = "8b7e2df..."

ls = LabelStudio(
    base_url=BASE_URL,
    api_key=API_KEY
)
# Organization ID is available at /organization page
ORG_ID = 1

# License data (status, usage analytics, user limits, etc.)
# https://api.labelstud.io/api-reference/api-reference/billing/info
print(ls.billing.info())

# Retrieve license details by user ID / email
# Validate active status of the license
# https://api.labelstud.io/api-reference/api-reference/organizations/members/get
user_id = None
for user in ls.users.list():
    if user.email == 'test1@test.com':
        member = ls.organizations.members.get(ORG_ID, user_pk=user.id)
        is_active = member.role not in ('DI', 'NO')
        if is_active:
            print(f'User {user.email} has ACTIVE license')
        else:
            print(f'User {user.email} has INACTIVE license')
        user_id = user.id
        break
            
# Active user
ls.organizations.members.update(ORG_ID, user_id=user_id, role="AN")

# Deactivate user
ls.organizations.members.update(ORG_ID, user_id=user_id, role="DI")

# Get current user token
print(ls.users.get_token())

# Reset user token
new_token = ls.users.reset_token()