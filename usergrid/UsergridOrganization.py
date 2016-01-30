class UsergridOrganization(object):
    def __init__(self, org_name, client):
        self.org_name = org_name
        self.client = client

    def application(self, app_name):
        return UsergridApplication(app_name, client=self.client)

    def app(self, app_name):
        return self.application(app_name)

