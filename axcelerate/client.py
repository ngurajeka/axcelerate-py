import requests
from requests import Response

BASE_URL = 'https://admin.axcelerate.com.au/api'


class Client(object):

    def __init__(self, wstoken: str, apitoken: str):
        self.wstoken = wstoken
        self.apitoken = apitoken

    def get(self, url: str) -> Response:
        url = '%s/%s' % (BASE_URL, url)
        r = requests.get(url, headers={
            'wstoken': self.wstoken,
            'apitoken': self.apitoken,
        })
        return r

    def post(self, url: str, payload: dict) -> Response:
        url = '%s/%s' % (BASE_URL, url)
        r = requests.post(url, data=payload, headers={
            'wstoken': self.wstoken,
            'apitoken': self.apitoken,
        })
        return r
