
__author__ = 'Jeff West @ ApigeeCorporation'

magement_org_url_template = "{api_url}/management/organizations/{org_name}"
management_org_list_apps_url_template = "{api_url}/management/organizations/{org_name}/applications"
management_app_url_template = "{api_url}/management/organizations/{org_name}/applications/{app_name}"
org_token_url_template = "{api_url}/management/token"
app_token_url_template = "{api_url}/{org_name}/{app_name}/token"
org_url_template = "{api_url}/{org_name}/"
app_url_template = "{api_url}/{org_name}/{app_name}"
collection_url_template = "{api_url}/{org_name}/{app_name}/{collection}"
collection_query_url_template = "{api_url}/{org_name}/{app_name}/{collection}?ql={ql}&limit={limit}"
get_entity_url_template = "{api_url}/{org_name}/{app_name}/{collection}/{uuid}&connections=none"
put_entity_url_template = "{api_url}/{org_name}/{app_name}/{collection}/{uuid}"

