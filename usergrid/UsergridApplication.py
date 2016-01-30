import logging


from usergrid import UsergridError, UsergridCollection
from usergrid.app_templates import app_url_template


class UsergridApplication(object):
    def __init__(self, app_name, client):
        self.app_name = app_name
        self.client = client
        self.logger = logging.getLogger('usergrid.UsergridClient')

    def list_collections(self):
        url = app_url_template.format(app_name=self.app_name,
                                      **self.client.url_data)
        r = self.client.get(url)

        if r.status_code == 200:
            api_response = r.json()
            collection_list = api_response.get('entities')[0].get('metadata', {}).get('collections', {})
            collections = {}

            for collection_name in collection_list:
                collections[collection_name] = UsergridCollection(self.client.org_name,
                                                                  self.app_name,
                                                                  collection_name,
                                                                  self.client)

            return collections

        else:
            raise UsergridError(message='Unable to post to list collections',
                                status_code=r.status_code,
                                api_response=r,
                                url=url)

    def collection(self, collection_name):
        return UsergridCollection(self.client.org_name,
                                  self.app_name,
                                  collection_name,
                                  self.client)

    def authenticate_app_client(self,
                                **kwargs):

        return self.client.authenticate_app_client(self.app_name, **kwargs)
