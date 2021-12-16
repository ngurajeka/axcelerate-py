import requests
from requests import Response

from axcelerate.file import File

BASE_URL = 'https://admin.axcelerate.com.au/api'


class Client(object):

    def __init__(self, wstoken: str, apitoken: str):
        self.wstoken = wstoken
        self.apitoken = apitoken
        self.base_url = BASE_URL

    def set_base_url(self, base_url):
        self.base_url = base_url

    @property
    def headers(self):
        return {
            'wstoken': self.wstoken,
            'apitoken': self.apitoken,
        }

    def get(self, url: str) -> Response:
        url = '%s/%s' % (self.base_url, url)
        return requests.get(url, headers=self.headers)

    def post(self, url: str, payload: dict) -> Response:
        url = '%s/%s' % (self.base_url, url)
        return requests.post(url, data=payload, headers=self.headers)

    def upload(self, url: str, payload: dict, file: File) -> Response:
        url = '%s/%s' % (self.base_url, url)
        files = {
            'addFile': (
                file.filename,
                open(file.location, 'rb'),
                file.filetype,
            )
        }
        return requests.post(url, data=payload, files=files, headers=self.headers)
