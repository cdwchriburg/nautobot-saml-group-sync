"""Additional functions to process an Azure user."""

# Can find group ID for Azure AD by:
#   Going to https://myaccount.microsoft.com/groups/groups-i-belong-to
#   Click on group name
#   Look at URL bar - group ID is in URL
#

# Group ID to Name Mapping. Only these groups will be created/used in Nautobot
AAD_GROUP_NAME_MAPPING = {
    "31bd75ed-adf3-425c-dfaf-1ad5fa51adfz": "abcXYZgroupName",
    "b5d61adf-1dfe-4dfa-adf5-4adfa41ad56a": "DEFghigroupName2"
}

# Only these groups will be permitted to login
LOGIN_ALLOWED_GROUPS = ["abcXYZgroupName", "DEFghigroupName2"]

# These groups will be set to Superuser status
SUPERUSER_GROUPS = ["abcXYZgroupName"]

# These groups will be set to Staff status
STAFF_GROUPS = ["abcXYZgroupName"]



import logging
from django.contrib.auth.models import Group

logger = logging.getLogger(__name__)
ROLES_GROUP_NAME = "http://schemas.microsoft.com/ws/2008/06/identity/claims/groups"

class AuthFailed(Exception): 
    pass

def set_role(uid, user=None, response=None, *args, **kwargs):  # pylint: disable=keyword-arg-before-vararg, unused-argument
    """Sync the users groups from Azure and set staff/superuser as appropriate."""
    if user and response and response['attributes'].get(ROLES_GROUP_NAME, False):
        group_memberships = response['attributes'].get(ROLES_GROUP_NAME)

        is_staff = False
        is_superuser = False
        logger.debug("User %s is a member of %s", uid, {", ".join(group_memberships)})

        group_ids = []
        for group in group_memberships:
            # Skip group if we don't have a mapping for it
            if group not in AAD_GROUP_NAME_MAPPING:
                continue

            if AAD_GROUP_NAME_MAPPING[group] in SUPERUSER_GROUPS:
                is_superuser = True
            if AAD_GROUP_NAME_MAPPING[group] in STAFF_GROUPS:
                is_staff = True
            group_ids.append(Group.objects.get_or_create(name=AAD_GROUP_NAME_MAPPING[group])[0].id)

        user.groups.set(group_ids)
        user.is_superuser = is_superuser
        user.is_staff = is_staff
        user.save()
    else:
        logger.debug("Did not receive roles from Azure, response: %s", response)
        raise AuthFailed(f"Didn't recieve roles from SAML.\nresponse: {response}") 

def verify_user_allowed_login(uid, user=None, response=None, *args, **kwargs):  # pylint: disable=keyword-arg-before-vararg, unused-argument
    """ Validate the user is in a group that is allowed to use the app"""
    if response and response['attributes'].get(ROLES_GROUP_NAME, False):
        group_memberships = response['attributes'].get(ROLES_GROUP_NAME)

        is_allowed_login = False
        logger.debug("User %s is a member of %s", uid, {", ".join(group_memberships)})

        group_ids = []
        for group in group_memberships:
            # Skip group if we don't have a mapping for it
            if group not in AAD_GROUP_NAME_MAPPING:
                continue

            if AAD_GROUP_NAME_MAPPING[group] in LOGIN_ALLOWED_GROUPS:
                is_allowed_login = True

        if not is_allowed_login:
            raise AuthFailed(f"User {uid} is not allowed to login.\n\nUser must be in one of the following groups:\n{LOGIN_ALLOWED_GROUPS}")
    else:
        logger.debug("Did not receive roles from Azure, response: %s", response)
        raise AuthFailed(f"Didn't recieve roles from SAML.\nresponse: {response}") 

