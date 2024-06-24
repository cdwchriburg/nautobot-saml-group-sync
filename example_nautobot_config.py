

# The most important setting. List the Entity ID, SSO URL, and x.509 public key certificate
# for each provider that you app wants to support. We are only supporting Google for this
# example.
SOCIAL_AUTH_SAML_ENABLED_IDPS = {
    "AzureAD": {
        "entity_id": AAD_ENTITY_ID,
        "url": AAD_SSO_URL,
        "x509cert": AAD_CERTIFICATE,
        # These are used to map to User object fields in Nautobot using Azure AD attribute fields returned from SAML
        # Left side is Nautobot variable name, right side is name of attribute returned from Azure AD in SAML
        "attr_user_permanent_id": "name_id",
        "attr_username": "name_id",
        "attr_first_name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname",
        "attr_last_name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname",
        "attr_email": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress",
    }
}




# Group mappings defined in saml_group_sync.py file (in /opt/nautobot)
#
# Adjust default pipline to add custom group sync from SAML/Azure AD groups
SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    "social_core.pipeline.user.get_username",
    "saml_group_sync.verify_user_allowed_login",
    "social_core.pipeline.user.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",
    "saml_group_sync.set_role",
)
