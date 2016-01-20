import json
import logging
import os
import traceback
import requests
import time

__author__ = 'Jeff West @ ApigeeCorporation'

logger = logging.getLogger('usergrid')

management_org_url_template = "{api_url}/management/organizations/{org_name}"
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


class UsergridConnectionProfile(object):
    def __init__(self,
                 profile_name='default',
                 directory=os.getenv('HOME') + '/.usergrid'):
        self.profile_name = profile_name
        self.directory = directory

        file_path = os.pathsep.join([directory, profile_name, '.json'])

        if not os.path.exists(file_path):
            raise ValueError('Profile not found in file=[%s]' % file_path)

        with open(file_path, 'r') as f:
            self.profile = json.load(f)

    def get_endpoint_data(self):
        return self.profile.get('endpoint')

    def get_credentials(self, org_name):
        return self.profile.get('credentials', {}).get(org_name)


class UsergridError(Exception):
    def __init__(self, message, status_code, api_response=None, url=None, data=None):
        super(UsergridError, self).__init__(message)
        self.status_code = status_code
        self.api_response = api_response
        self.url = url
        self.data = data

    def __str__(self):
        return 'HTTP [%s] %s: %s' % (self.status_code, self.url, self.message)


class UsergridClient(object):
    def __init__(self, api_url, org_name, access_token=None):
        self.access_token = access_token
        self.api_url = api_url
        self.org_name = org_name

        if access_token is not None:
            self.headers = {'Authorization': 'Bearer %s' % access_token}
        else:
            self.headers = {}

        self.url_data = {
            'api_url': api_url,
            'org_name': org_name
        }

    def __str__(self):
        return json.dumps({
            'api_url': self.api_url,
            'org_name': self.org_name,
            'access_token': self.access_token
        })

    @staticmethod
    def _validate_credentials(client_credentials, user_credentials):
        if user_credentials is None and client_credentials is None:
            raise ValueError('Need one of user_credentials or client_credentials to get a token!')

        if user_credentials is not None:
            if 'username' not in user_credentials:
                raise ValueError('user_credentials requires username and password')

            if 'password' not in user_credentials:
                raise ValueError('user_credentials requires username and password')

        if client_credentials is not None:
            if 'client_id' not in client_credentials:
                raise ValueError('client_credentials requires client_id and client_secret')

            if 'client_secret' not in client_credentials:
                raise ValueError('client_credentials requires client_id and client_secret')

    def authenticate_management_client(self,
                                       user_credentials=None,
                                       client_credentials=None):

        self._validate_credentials(client_credentials, user_credentials)

        url = org_token_url_template.format(**self.url_data)

        if client_credentials is not None:
            token = self._client_token_request(url, client_credentials)
        else:
            token = self._password_token_request(url, user_credentials)

        self.access_token = token
        self.headers['Authorization'] = 'Bearer %s' % self.access_token

        return token

    def authenticate_app_client(self,
                                app,
                                user_credentials=None,
                                client_credentials=None):

        self._validate_credentials(client_credentials, user_credentials)

        if app is None:
            raise ValueError('App cannot be None')

        url = app_token_url_template.format(app_name=app, **self.url_data)

        if client_credentials is not None:
            token = self._client_token_request(url, client_credentials)
        else:
            token = self._password_token_request(url, user_credentials)

        self.access_token = token
        self.headers['Authorization'] = 'Bearer %s' % self.access_token

        return token

    @staticmethod
    def _token_request(url, token_request):

        r = requests.post(url, data=json.dumps(token_request))

        if r.status_code == 200:
            response = r.json()
            return response.get('access_token')
        else:
            raise UsergridError(message='Unable to get token',
                                status_code=r.status_code,
                                api_response=r,
                                url=url)

    def _client_token_request(self, url, client_credentials=None):

        token_request = {
            'grant_type': 'client_credentials',
        }

        token_request.update(client_credentials)

        return self._token_request(url, token_request)

    def _password_token_request(self, url, user_credentials):

        token_request = {
            'grant_type': 'password',
        }

        token_request.update(user_credentials)

        return self._token_request(url, token_request)

    def get_token(self):
        return self.access_token

    def set_token(self, token):
        self.access_token = token

    def get(self, url, **kwargs):
        r = requests.get(url, headers=self.headers)
        return r

    def post(self, url, data, **kwargs):
        r = requests.post(url, data=json.dumps(data), headers=self.headers)
        return r

    def put(self, url, data, **kwargs):
        r = requests.put(url, data=json.dumps(data), headers=self.headers)
        return r

    def list_apps(self):

        url = management_org_list_apps_url_template.format(**self.url_data)

        r = self.get(url)

        if r.status_code == 200:
            response = {}

            for org_app, app_uuid in r.json().get('data').iteritems():
                app_name = org_app.split('/')[1]
                response[app_name] = UsergridApplication(app_name, self)

            return response

        else:
            raise UsergridError(message='Unable to list applications for org=[%s]' % self.org_name,
                                status_code=r.status_code,
                                api_response=r,
                                url=url)

    def organization(self, org_name):
        return UsergridOrganization(org_name, self)

    def org(self, org_name):
        return self.organization(org_name)


class UsergridEntity(object):
    def __init__(self, org_name, app_name, collection_name, data, client):
        self.org_name = org_name
        self.app_name = app_name
        self.collection_name = collection_name
        self.data = data
        self.client = client

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


class UsergridConnection(object):
    def __init__(self, source_entity, verb, target_entity):
        self.source_entity = source_entity
        self.verb = verb
        self.target_entity = target_entity


class UsergridOrganization(object):
    def __init__(self, org_name, client):
        self.org_name = org_name
        self.client = client

    def application(self, app_name):
        return UsergridApplication(app_name, client=self.client)

    def app(self, app_name):
        return self.application(app_name)


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


class UsergridApplication(object):
    def __init__(self, app_name, client):
        self.app_name = app_name
        self.client = client

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


class UsergridQuery(object):
    def __init__(self,
                 url,
                 operation='GET',
                 headers=None,
                 data=None):

        if not data:
            data = {}
        if not headers:
            headers = {}

        self.total_retrieved = 0
        self.logger = logging.getLogger('usergrid.UsergridQuery')
        self.data = data
        self.headers = headers
        self.url = url
        self.operation = operation
        self.next_cursor = None
        self.entities = []
        self.count_retrieved = 0
        self._pos = 0
        self.last_response = None
        self.sleep_time = 1
        self.session = None

    def _get_next_response(self, attempts=0):

        if self.session is None:
            self.session = requests.Session()

        try:
            if self.operation == 'PUT':
                op = self.session.put
            elif self.operation == 'DELETE':
                op = self.session.delete
            else:
                op = self.session.get

            target_url = self.url

            if self.next_cursor is not None:
                delim = '&' if '?' in target_url else '?'
                target_url = '%s%scursor=%s' % (self.url, delim, self.next_cursor)

            logger.debug('Operation=[%s] URL=[%s]' % (self.operation, target_url))

            r = op(target_url, data=json.dumps(self.data), headers=self.headers)

            if r.status_code == 200:
                r_json = r.json()
                self.logger.info('Retrieved [%s] entities in %s' % (len(r_json.get('entities', [])), r.elapsed))
                return r_json

            elif r.status_code in [401, 404] and 'service_resource_not_found' in r.text:
                self.logger.warn('Query Not Found [%s] on URL=[%s]: %s' % (r.status_code, target_url, r.text))
                return None

            else:
                if attempts < 10:
                    self.logger.info('URL=[%s] code=[%s], response: %s' % (target_url, r.status_code, r.text))
                    self.logger.warning('Sleeping %s after HTTP [%s] for retry attempt=[%s]' % (
                        self.sleep_time, r.status_code, attempts))
                    time.sleep(self.sleep_time)

                    return self._get_next_response(attempts=attempts + 1)

                else:
                    raise SystemError('Unable to get next response after %s attempts' % attempts)

        except:
            print traceback.format_exc()

    def next(self):

        if self.last_response is None:
            logger.debug('getting first page, url=[%s]' % self.url)

            self._process_next_page()

        elif self._pos >= len(self.entities) > 0 and self.next_cursor is not None:
            logger.debug('getting next page, count=[%s] url=[%s], cursor=[%s]' % (
                self.count_retrieved, self.url, self.next_cursor))

            self._process_next_page()

        if self._pos < len(self.entities):
            response = self.entities[self._pos]
            self._pos += 1
            return response

        raise StopIteration

    def __iter__(self):
        return self

    def _process_next_page(self, attempts=0):

        api_response = self._get_next_response()

        if api_response is None:
            logger.warn('Unable to retrieve query results from url=[%s]' % self.url)
            api_response = {}

        self.last_response = api_response

        self.entities = api_response.get('entities', [])
        self.next_cursor = api_response.get('cursor', None)
        self._pos = 0
        self.count_retrieved += len(self.entities)

        if self.next_cursor is None:
            logger.info('no cursor in response. Total=[%s] url=[%s]' % (self.count_retrieved, self.url))
