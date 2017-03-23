#!/usr/bin/python3

from credentials import Credentials
from datetime import date, datetime
from json import dumps
from urllib.parse import urlencode, ParseResult, parse_qsl, unquote, urlparse, ParseResult
from urllib.request import Request, urlopen, unquote, urlparse
from urllib.error import URLError, HTTPError
from http.client import HTTPResponse
from os.path import isfile
import argparse
import base64
import http.client
import json
import math
import os
import urllib.parse

# try:
#     from urllib import urlencode, unquote
#     from urlparse import urlparse, parse_qsl, ParseResult
# except ImportError:
#     # Python 3 fallback
#     from urllib.parse import (
#         urlencode, unquote, urlparse, parse_qsl, ParseResult
#     )

# REF: https://wakatime.com/developers#users

CREDENTIALS = "credentials.json"
AUTH_BASE_URL = "https://wakatime.com/oauth/authorize"
BASE_URL = "https://wakatime.com/api/v1/"
REDIRECT_URL = "https://wakatime.com/oauth/test"
TOKEN_URL = "https://wakatime.com/oauth/token"
# Client id = App id
CLIENT_ID_KEY = "wakatime_client_id"
SECRET_KEY = "wakatime_secret"
TOKEN_KEY = "wakatime_access_token"
REFRESH_TOKEN_KEY = "wakatime_refresh_token"

class WakatimeManager(object):

    def __init__(self):
        credentialsData = None
        # Load token if available from previous session.
        filepath = self.credentialsFilePath()
        print('Credentials filepath: ', filepath)
        if isfile(filepath):
            with open(filepath, 'r') as f:
                try:
                    credentialsData = json.load(f)
                    self.clientId = credentialsData[CLIENT_ID_KEY]
                    self.secret = credentialsData[SECRET_KEY]
                    print("API KEY loaded: ", self.clientId)
                    print("SECRET loaded: ", self.secret)
                except:
                    pass
        # Request a new token.
        if credentialsData == None:
            credentialsData = {}

        try:
            self.clientId = credentialsData[CLIENT_ID_KEY]
        except KeyError:
            self.clientId = self.newClientId()
            if self.clientId == None:
                print('No client id entered. Exiting.')
                return
            self.saveCredential(CLIENT_ID_KEY, self.clientId)

        try:
            self.secret = credentialsData[SECRET_KEY]
        except KeyError:
            self.secret = self.newSecret()
            if self.secret == None:
                print('No app secret entered. Exiting.')
                return
            self.saveCredential(SECRET_KEY, self.secret)

        # TODO: Clean up
        try:
            token = credentialsData[TOKEN_KEY]
            if token != None:
                self.token = token
                print("Token loaded: ", self.token)
                return

            token = self.getNewToken()

            if token == None:
                print('No token entered. Exiting.')
            else:
                self.token = token
                self.saveCredential(TOKEN_KEY, self.token)
                print("Token saved: ", self.token)
        except KeyError:
            self.token = self.getNewToken()
            if self.token == None:
                print('No token entered. Exiting.')
                return
            self.saveCredential(TOKEN_KEY, self.token)
            print("New Token saved: ", self.token)


    def newClientId(self):
        # Client id = Wakatime app id
        key = input("Enter Wakatime App Id: ")
        return key

    def newSecret(self):
        key = input("Enter Wakatime App Secret: ")
        return key

    def credentialsFilePath(self):
        filepath = os.getenv('APPDATA')
        if filepath == None:
            return CREDENTIALS
        path = "{}{}", format(filepath), CREDENTIALS
        return path

    def saveCredential(self, key, value):
        # Save to a JSON file
        fileJson = None
        filepath = self.credentialsFilePath()
        if isfile(filepath):
            try:
                with open(filepath, 'r') as f:
                    fileJson = json.load(f)
            except json.decoder.JSONDecodeError as e:
                print("{}: Error loading credentials:{}".format(time.time(), e))
                fileJson = {}
        else:
            fileJson = {}
        if not key in fileJson:
            fileJson[key] = {}
        fileJson[key] = value
        with open(filepath, 'w') as f:
            json.dump(fileJson, f, indent=4)

    def getHours(self, repo, branches):
        # parser = argparse.ArgumentParser()
        # parser.add_argument("repo", type=str, help='Remote repository name.')
        # parser.add_argument("branches", type=str, help='Remote repository branches to update cards for. Comma separated.')
        # args = parser.parse_args()
        # repo = args.repo
        # branches = args.branches
        user_data = self.getCurrentUserInfo()
        created_at_string = user_data['data']['created_at']
        created_at_datetime = datetime.strptime(created_at_string, '%Y-%m-%dT%H:%M:%SZ')
        created_at = created_at_datetime.date()
        summary = self.getSummaries(created_at, repo, branches)
        # TODO: Convert branches to list
        seconds = self.grandTotalSeconds(summary, branches)
        hours = math.ceil(seconds/3600)
        return hours

    def grandTotalSeconds(self, summary_dict, branch):
        # Get list of data dicts, each containing a 'branches' key with
        #   a list of branches as strings
        grand_total_seconds = 0
        data_list = summary_dict['data']
        # print('Summary data list: ', data_list)
        for index in range(len(data_list)):
            data_dict = data_list[index]
            branch_list = data_dict['branches']
            for branch_dict in branch_list:
                branch_name = branch_dict['name']
                if branch_name == branch:
                    total_seconds_string = branch_dict['total_seconds']
                    total_seconds = int(total_seconds_string)
                    grand_total_seconds += total_seconds
                    print('Iterating at index: ', index, ' branch dict: ', branch_dict, " total seconds now: ", grand_total_seconds)

        return grand_total_seconds

    def getSummaries(self, createdAt, project, branches):
        creds = Credentials
        api_key = creds.wakatime_api_key
        api_bytes = bytes(api_key, 'utf-8')
        encoded_api_key = base64.b64encode(api_bytes,altchars=None)
        prepended_encoded_api_key = 'Basic '+ str(encoded_api_key, 'utf-8')
        url = 'https://wakatime.com/api/v1/'
        path = url + 'users/current/summaries'
        date_now = date.today()
        date_now_iso = date_now.isoformat()
        # Use users created at date
        date_past = createdAt
        date_past_iso = date_past.isoformat()
        params = {'start':date_past_iso, 'end': date_now_iso, 'project':project, 'branches':branches}
        path_with_params = self.add_url_params(path, params)
        headers = {'Authorization':prepended_encoded_api_key }
        req = Request(path_with_params, None, headers)
        print('Request path: ', path_with_params)
        try:
            response = urlopen(req)
        except HTTPError as e:
            print('The server couldn\'t fulfill the request.')
            print('Error code: ', e.code)
            print('Response: ', e.reason)
        except URLError as e:
            print('We failed to reach a server.')
            print('Reason: ', e.reason)
        else:
            readResponse = HTTPResponse.read(response)
            result = json.loads(readResponse.decode('utf-8'))
            # print('JSON: ', result)
            return result


    def getDataFor(self, path):
        # Using API Key
        # creds = Credentials
        # api_key = creds.api_key
        # api_bytes = bytes(api_key, 'utf-8')
        # encoded_api_key = base64.b64encode(api_bytes, altchars=None)
        # prepended_encoded_api_key = 'Basic ' + str(encoded_api_key, 'utf-8')
        # url = 'https://wakatime.com/api/v1/'
        # path = url + 'users/current/'
        # headers = {'Authorization': prepended_encoded_api_key}

        # Using Tokens
        url = BASE_URL + path
        prepended_encoded_token = 'Bearer ' + self.token
        headers = {'Authorization':prepended_encoded_token}

        req = Request(url, None, headers)
        print('getDataFor: ', url)
        try:
            response = urlopen(req)
        except HTTPError as e:
            print('The server couldn\'t fulfill the request.')
            print('Error code: ', e.code)
            print('Response: ', e.reason)
        except URLError as e:
            print('We failed to reach a server.')
            print('Reason: ', e.reason)
        else:
            readResponse = HTTPResponse.read(response)
            result = json.loads(readResponse.decode('utf-8'))
            # print('JSON: ', result)
            return result

    def getNewToken(self):
        # First Leg
        params = {'client_id':self.clientId,
                  'response_type':'code',
                  'redirect_uri':REDIRECT_URL,
                  'scope':'email,read_logged_time'}
        url = self.add_url_params(AUTH_BASE_URL, params)
        code = input('Goto the following address into a browser: ' + url + ' then enter the token here: ')

        # Second Leg
        code_params = {'client_id':self.clientId,
                       'client_secret':self.secret,
                       'code':code,
                       'grant_type':'authorization_code',
                       'redirect_uri':REDIRECT_URL}
        request = Request(TOKEN_URL, urlencode(code_params).encode())
        try:
            response = urlopen(request)
        except HTTPError as e:
            print('The server couldn\'t fulfill the request.')
            print('Error code: ', e.code)
            print('Response: ', e.reason)
        except URLError as e:
            print('We failed to reach a server.')
            print('Reason: ', e.reason)
        else:
            readResponse = HTTPResponse.read(response)
            # returned as bytes
            result = json.loads(readResponse.decode('utf-8'))

            # SAMPLE RETURN
            # {
            #     'uid': '9049653a-875f-4931-9ccb-f55c690d7ed8',
            #     'token_type': 'bearer',
            #     'scope': 'email,read_logged_time',
            #     'expires_in': 5184000,
            #     'refresh_token': 'ref_vFTwk27pNMWXyuyCcvgySBnVXcpnSZxuMAUkUNHyOvJGLRAYclJjc0HjkYlSgn9Mnm2BxFagSjGNPpFG',
            #     'access_token': 'sec_UmBllZHU7vufAtoQacAh67CPEu1WNu2ls9mXaGCutvzePZAW1YmAYaYYMCjgxwntXsfGbRMFteyBMSEj'
            # }

            print('wakatime_manager: getNewToken: json: ', result)
            # TODO: Better way to save and recall refresh token
            self.saveCredential(REFRESH_TOKEN_KEY,result['refresh_token'])

        return result['access_token']

    def add_url_params(self, url, params):
        """ Add GET params to provided URL being aware of existing.

        :param url: string of target URL
        :param params: dict containing requested params to be added
        :return: string with updated URL

        >> url = 'http://stackoverflow.com/test?answers=true'
        >> new_params = {'answers': False, 'data': ['some','values']}
        >> add_url_params(url, new_params)
        'http://stackoverflow.com/test?data=some&data=values&answers=false'
        """
        # Unquoting URL first so we don't loose existing args
        url = unquote(url)
        # Extracting url info
        parsed_url = urlparse(url)
        # Extracting URL arguments from parsed URL
        get_args = parsed_url.query
        # Converting URL arguments to dict
        parsed_get_args = dict(parse_qsl(get_args))
        # Merging URL arguments dict with new params
        parsed_get_args.update(params)

        # Bool and Dict values should be converted to json-friendly values
        # you may throw this part away if you don't like it :)
        parsed_get_args.update(
            {k: dumps(v) for k, v in parsed_get_args.items()
             if isinstance(v, (bool, dict))}
        )

        # Converting URL argument to proper query string
        encoded_get_args = urlencode(parsed_get_args, doseq=True)
        # Creating new parsed result object based on provided with new
        # URL arguments. Same thing happens inside of urlparse.
        new_url = ParseResult(
            parsed_url.scheme, parsed_url.netloc, parsed_url.path,
            parsed_url.params, encoded_get_args, parsed_url.fragment
        ).geturl()

        return new_url

# For self running
if __name__ == '__main__':
    wt = WakatimeManager()
    currentUser = wt.getDataFor("users/current")
    print('wakatime_manager: main: currentUser info: ', currentUser)