import json
import logging

import requests
from usergrid.path_templates import management_org_list_apps_url_template, org_token_url_template, \
    app_token_url_template

from usergrid import UsergridError, UsergridOrganization, UsergridApplication


class UsergridClient(object):
    def __init__(self, api_url, org_name, access_token=None):
        self.access_token = access_token
        self.api_url = api_url
        self.org_name = org_name
        self.logger = logging.getLogger('usergrid.UsergridClient')

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

