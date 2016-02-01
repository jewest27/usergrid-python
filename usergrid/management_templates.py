__author__ = 'Jeff West @ ApigeeCorporation'

management_base_url = '{base_url}/management'
management_org_url_template = "%s/organizations/{org_id}" % management_base_url
management_org_list_apps_url_template = "%s/applications" % management_org_url_template
management_app_url_template = "%s/applications/{app_id}" % management_org_url_template

org_token_url_template = "%s/token" % management_base_url
