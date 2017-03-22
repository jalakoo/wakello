#!/usr/bin/python3

from credentials import Credentials
from datetime import date, datetime
from json import dumps
from urllib.parse import urlencode, ParseResult, parse_qsl
from urllib.request import Request, urlopen, unquote, urlparse
from urllib.error import URLError, HTTPError
from http.client import HTTPResponse
import argparse
import base64
import json
import math

class WakatimeManager(object):

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
        api_key = creds.api_key
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


    def getCurrentUserInfo(self):
        creds = Credentials
        api_key = creds.api_key
        api_bytes = bytes(api_key, 'utf-8')
        encoded_api_key = base64.b64encode(api_bytes, altchars=None)
        prepended_encoded_api_key = 'Basic ' + str(encoded_api_key, 'utf-8')
        url = 'https://wakatime.com/api/v1/'
        path = url + 'users/current/'
        headers = {'Authorization': prepended_encoded_api_key}
        req = Request(path, None, headers)
        print('Request path: ', path)
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

    from json import dumps

    try:
        from urllib import urlencode, unquote
        from urlparse import urlparse, parse_qsl, ParseResult
    except ImportError:
        # Python 3 fallback
        from urllib.parse import (
            urlencode, unquote, urlparse, parse_qsl, ParseResult
        )


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
