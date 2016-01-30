import json


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
