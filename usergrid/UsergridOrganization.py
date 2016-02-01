from usergrid import UsergridApplication


class UsergridOrganization(object):
    def __init__(self, org_id, client):
        self.org_id = org_id
        self.client = client

    def application(self, app_id):
        return UsergridApplication(app_id, client=self.client)

    def app(self, app_id):
        return self.application(app_id)

