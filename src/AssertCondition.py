
from .Exceptions import StatusCodeAssertException

class AssertCondition:

    @staticmethod
    def statusCodeMatches(expected, response):
        if response.status_code == expected:
            return

        statusCode = response.status_code
        url = response.request.url
        response.close()
        raise StatusCodeAssertException(expected, statusCode, url)