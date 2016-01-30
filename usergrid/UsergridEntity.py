import json
import logging

from usergrid import UsergridError
from usergrid.app_templates import get_entity_url_template, put_entity_url_template


class UsergridEntity(object):
    def __init__(self, org_name, app_name, collection_name, data, client):
        self.org_name = org_name
        self.app_name = app_name
        self.collection_name = collection_name
        self.data = data
        self.client = client
        self.logger = logging.getLogger('usergrid.UsergridEntity')

    def __str__(self):
        return json.dumps(self.data)

    def get(self, client=None, **kwargs):
        url = get_entity_url_template.format(app_name=self.app_name,
                                             collection=self.collection_name,
                                             uuid=self.data['uuid'] if self.data['uuid'] is not None else self.data[
                                                 'name'],
                                             **self.client.url_data)
        if client:
            r = client.get(url, **kwargs)
        else:
            r = self.client.get(url, **kwargs)

        if r.status_code == 200:
            api_response = r.json()
            entity = api_response.get('entities')[0]
            self.data.update(entity)

        else:
            raise UsergridError(message='Unable to get entity',
                                status_code=r.status_code,
                                api_response=r,
                                url=url)

    def put(self, client=None, **kwargs):
        url = put_entity_url_template.format(app_name=self.app_name,
                                             collection=self.collection_name,
                                             uuid=self.data['uuid'] if self.data['uuid'] is not None else self.data[
                                                 'name'],
                                             **self.client.url_data)

        put_data = self.data.copy()

        if 'metadata' in put_data: put_data.pop('metadata')

        if client:
            r = client.put(url, data=put_data, **kwargs)
        else:
            r = self.client.put(url, data=put_data, **kwargs)

        if r.status_code == 200:
            api_response = r.json()
            entity = api_response.get('entities')[0]
            self.data.update(entity)

        else:
            raise UsergridError(message='Unable to put entity',
                                status_code=r.status_code,
                                data=put_data,
                                api_response=r,
                                url=url)

