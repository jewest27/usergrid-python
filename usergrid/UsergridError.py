

class UsergridError(Exception):

    def __init__(self, message, status_code, api_response=None, url=None, data=None):
        super(UsergridError, self).__init__(message)
        self.status_code = status_code
        self.api_response = api_response
        self.url = url
        self.data = data

    def __str__(self):
        return 'HTTP [%s] %s: %s' % (self.status_code, self.url, self.message)

