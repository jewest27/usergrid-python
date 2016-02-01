import json
from usergrid import Usergrid

__author__ = 'ApigeeCorporation'


def main():
    with open('/Users/ApigeeCorporation/.usergrid/credentials/org_jwest1.json', 'r') as f:
        org_credentials = json.load(f)

    with open('/Users/ApigeeCorporation/.usergrid/credentials/app_a127.json', 'r') as f:
        a127 = json.load(f)

    Usergrid.init(org_id='jwest1',
                  app_id='sandbox')

    response = Usergrid.DELETE('pets', 'max')
    if not response.ok:
        print 'Failed to delete max: %s' % response
        exit()

    response = Usergrid.DELETE('owners', 'jeff')
    if not response.ok:
        print 'Failed to delete Jeff: %s' % response
        exit()

    response = Usergrid.POST('pets', {'name': 'max'})

    if response.ok:
        pet = response.first()
        print pet
        response = Usergrid.POST('owners', {'name': 'jeff'})

        if response.ok:
            owner = response.first()
            print owner
            response = pet.connect('ownedBy', owner)

            if response.ok:
                print 'Connected!'

                response = pet.disconnect('ownedBy', owner)

                if response.ok:
                    print 'all done!'
                else:
                    print response
            else:
                print 'failed to connect: %s' % response

        else:
            print 'Failed to create Jeff: %s' % response

    else:
        print response


main()
