
class UsergridCollection(object):
    def __init__(self, org_name, app_name, collection_name, client):
        self.org_name = org_name
        self.app_name = app_name
        self.collection_name = collection_name
        self.client = client

    def __str__(self):
        return json.dumps({
            'org_name': self.org_name,
            'app_name': self.app_name,
            'collection_name': self.collection_name,
        })

    def entity(self, uuid):
        pass

    def entity_from_data(self, data):
        return UsergridEntity(org_name=self.org_name,
                              app_name=self.app_name,
                              collection_name=self.collection_name,
                              data=data,
                              client=self.client)

    def query(self, ql='select *', limit=100):
        url = collection_query_url_template.format(app_name=self.app_name,
                                                   ql=ql,
                                                   limit=limit,
                                                   collection=self.collection_name,
                                                   **self.client.url_data)

        return UsergridQuery(url, headers=self.client.headers)

    def entities(self, **kwargs):
        return self.query(**kwargs)

    def post(self, entity, **kwargs):
        url = collection_url_template.format(collection=self.collection_name,
                                             app_name=self.app_name,
                                             **self.client.url_data)

        r = self.client.post(url, data=entity, **kwargs)

        if r.status_code == 200:
            api_response = r.json()
            entity = api_response.get('entities')[0]
            e = UsergridEntity(org_name=self.org_name,
                               app_name=self.app_name,
                               collection_name=self.collection_name,
                               data=entity,
                               client=self.client)
            return e

        else:
            raise UsergridError(message='Unable to post to collection name=[%s]' % self.collection_name,
                                status_code=r.status_code,
                                data=entity,
                                api_response=r,
                                url=url)

