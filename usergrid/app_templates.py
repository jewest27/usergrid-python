
__author__ = 'Jeff West @ ApigeeCorporation'

org_url_template = "{api_url}/{org_name}/"
app_url_template = "{api_url}/{org_name}/{app_name}"

app_token_url_template = "{api_url}/{org_name}/{app_name}/token"

collection_url_template = "{api_url}/{org_name}/{app_name}/{collection}"
collection_query_url_template = "{api_url}/{org_name}/{app_name}/{collection}?ql={ql}&limit={limit}"
get_entity_url_template = "{api_url}/{org_name}/{app_name}/{collection}/{uuid}&connections=none"
put_entity_url_template = "{api_url}/{org_name}/{app_name}/{collection}/{uuid}"

