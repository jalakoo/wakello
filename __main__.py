#!/usr/bin/python3

from credentials import Credentials
import base64
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from http.client import HTTPResponse
import json

def main():
    creds = Credentials
    api_key = creds.api_key
    api_bytes = bytes(api_key, 'utf-8')
    encoded_api_key = base64.b64encode(api_bytes,altchars=None)
    prepended_encoded_api_key = 'Basic '+ str(encoded_api_key, 'utf-8')
    url = 'https://wakatime.com/api/v1/'
    testPath = url + 'users/current'
    headers = {'Authorization':prepended_encoded_api_key }
    req = Request(testPath, None, headers)
    try:
        response = urlopen(req)
    except HTTPError as e:
        print('The server couldn\'t fulfill the request.')
        print('Error code: ', e.code)
    except URLError as e:
        print('We failed to reach a server.')
        print('Reason: ', e.reason)
    else:
        print('Response: ', response)
        print('Read: ', HTTPResponse.read(response))

        # response_data = HTTPResponse.read(response)
        # response_string = base64.b64decode(response_data)
        # print('Response string: ', response_string)
        # result = json.loads(response.read().decode('utf-8'))
        # print('Read as JSON: ', result)


if __name__ == '__main__':
    main()
