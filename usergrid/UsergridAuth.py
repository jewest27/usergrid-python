import json

import requests

from usergrid.app_templates import app_token_url_template

from usergrid.management_templates import org_token_url_template


class UsergridAuth:
    def __init__(self,
                 grant_type,
                 url_template,
                 username=None,
                 password=None,
                 client_id=None,
                 client_secret=None,
                 token_ttl_seconds=86400):

        self.grant_type = grant_type
        self.username = username
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_ttl_seconds = token_ttl_seconds
        self.url_template = url_template
        self.access_token = None

    def get_token_request(self):
        if self.grant_type == 'client_credentials':
            return {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'ttl': self.token_ttl_seconds * 1000
            }
        elif self.grant_type == 'password':
            return {
                'grant_type': 'password',
                'username': self.username,
                'password': self.password,
                'ttl': self.token_ttl_seconds * 1000
            }

        else:
            raise ValueError('Unspecified/unknown grant type: %s' % self.grant_type)

    def authenticate(self, client):
        token_request = self.get_token_request()

        url = self.url_template.format(**client.url_data)

        r = requests.post(url, data=json.dumps(token_request))

        if r.status_code == 200:
            response = r.json()
            self.access_token = response.get('access_token')

        else:
            raise ValueError('Unable to authenticate: %s' % r.text)


class UsergridOrgAuth(UsergridAuth):
    def __init__(self, client_id, client_secret, token_ttl_seconds=86400):
        UsergridAuth.__init__(self,
                              grant_type='client_credentials',
                              url_template=org_token_url_template,
                              client_id=client_id,
                              client_secret=client_secret,
                              token_ttl_seconds=token_ttl_seconds)


class UsergridAppAuth(UsergridAuth):
    def __init__(self, client_id, client_secret, token_ttl_seconds=86400):
        UsergridAuth.__init__(self,
                              grant_type='client_credentials',
                              url_template=app_token_url_template,
                              client_id=client_id,
                              client_secret=client_secret,
                              token_ttl_seconds=token_ttl_seconds)


class UsergridUserAuth(UsergridAuth):
    def __init__(self, username, password, token_ttl_seconds=86400):
        UsergridAuth.__init__(self,
                              grant_type='password',
                              url_template=app_token_url_template,
                              username=username,
                              password=password,
                              token_ttl_seconds=token_ttl_seconds)
