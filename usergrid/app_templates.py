__author__ = 'Jeff West @ ApigeeCorporation'

org_url_template = "{base_url}/{org_id}"
app_url_template = "%s/{app_id}" % org_url_template

app_token_url_template = "%s/token" % app_url_template

collection_url_template = "%s/{collection}" % app_url_template
collection_query_url_template = "%s?ql={ql}&limit={limit}" % collection_url_template

post_collection_url_template = collection_url_template
entity_url_template = "%s/{uuid_name}" % collection_url_template
get_entity_url_template = "%s?connections={connections}" % entity_url_template
put_entity_url_template = entity_url_template
delete_entity_url_template = entity_url_template

assign_role_url_template = '%s/roles/{role_uuid_name}/{entity_type}/{entity_uuid_name}' % app_url_template

connect_entities_by_type_template = '%s/{from_collection}/{from_uuid_name}/{relationship}/{to_collection}/{to_uuid_name}' % app_url_template