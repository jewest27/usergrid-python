import json
import time
from usergrid import UsergridClient

__author__ = 'ApigeeCorporation'


def main():

    with open('/Users/ApigeeCorporation/.usergrid/credentials/org_jwest1.json', 'r') as f:
        org_credentials = json.load(f)

    with open('/Users/ApigeeCorporation/.usergrid/credentials/app_a127.json', 'r') as f:
        a127 = json.load(f)

    client = UsergridClient('https://api.usergrid.com', 'jwest1')
    token = client.authenticate_management_client(client_credentials=org_credentials)
    print token

    # a127_app = client.application('a127')
    # token = a127_app.authenticate_app_client(client_credentials=a127)
    # print token
    #
    app = client.get_application('a127')
    c = app.collection('stuff')
    new_entity = c.post({'foo': 'bar'})
    print new_entity.data['uuid']
    new_entity.data['jeff'] = 'west'
    new_entity.put()
    print new_entity.data['uuid']
    print new_entity.data['jeff']

    apps = client.list_apps()

    for app_name, app in apps.iteritems():
        print app_name

        collections = app.list_collections()

        for collection_name, collection in collections.iteritems():
            print collection

            for e in collection.entities(limit=10):
                print e
                time.sleep(1)


main()
