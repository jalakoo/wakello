#!/usr/bin/python3

# REFERENCES
# https://github.com/sarumont/py-trello
# http://stackoverflow.com/questions/33464487/trello-api-simply-getting-the-contents-of-a-list

from credentials import Credentials
from os.path import isfile
from urllib.parse import urlencode, ParseResult, parse_qsl
from urllib.request import Request, urlopen, unquote, urlparse
from urllib.error import URLError, HTTPError
from http.client import HTTPResponse
import json
import os
import time
import argparse

BASE_URL = "https://api.trello.com/1/"
CREDENTIALS = "credentials.json"
TOKEN_KEY = "trello_token"

class TrelloManager(object):

    def __init__(self):
        trelloData = None
        # Load token if available from previous session.
        filepath = self.credentialsFilePath()
        print('Credentials filepath: ', filepath)
        if isfile(filepath):
            with open(filepath, 'r') as f:
                try:
                    trelloData = json.load(f)
                    self.token = trelloData[TOKEN_KEY]
                    print("Token loaded: ", self.token)
                except:
                    pass
        # Request a new token.
        if trelloData == None:
            token = self.getNewToken()
            self.saveToken(token)
            self.token = token
            print("New token added: ", self.token)

    def credentialsFilePath(self):
        filepath = os.getenv('APPDATA')
        if filepath == None:
            return CREDENTIALS
        path = "{}{}", format(filepath), CREDENTIALS
        return path

    def saveToken(self, token):
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
        if not TOKEN_KEY in fileJson:
            fileJson[TOKEN_KEY] = {}
        fileJson[TOKEN_KEY] = token
        with open(filepath, 'w') as f:
            json.dump(fileJson, f, indent=4)

    def getNewToken(self):
        # Ask user to go to a site and get token - as they will need to be logged into Trello to request it.
        creds = Credentials()
        url = BASE_URL + "connect?key=" + creds.trello_api_key + "&name=Wakello&response_type=token"
        token = input("Paste this page in a browser: " + url + ". Then enter token here: ")
        return token

    def getListCards(self, listId):
        url = BASE_URL + "lists/" + listId + "/cards?key=" + Credentials().trello_api_key + "&token=" + self.token
        headers = {}
        req = Request(url, None, headers)
        print('Request url: ', url)
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
            # print('Response: {} {}', readResponse, type(readResponse))
            result = json.loads(readResponse.decode('utf-8'))
            # print('JSON: ', result)
            return result

    # def add_url_params(self, url, params):
    #     """ Add GET params to provided URL being aware of existing.
    #
    #     :param url: string of target URL
    #     :param params: dict containing requested params to be added
    #     :return: string with updated URL
    #
    #     >> url = 'http://stackoverflow.com/test?answers=true'
    #     >> new_params = {'answers': False, 'data': ['some','values']}
    #     >> add_url_params(url, new_params)
    #     'http://stackoverflow.com/test?data=some&data=values&answers=false'
    #     """
    #     # Unquoting URL first so we don't loose existing args
    #     url = unquote(url)
    #     # Extracting url info
    #     parsed_url = urlparse(url)
    #     # Extracting URL arguments from parsed URL
    #     get_args = parsed_url.query
    #     # Converting URL arguments to dict
    #     parsed_get_args = dict(parse_qsl(get_args))
    #     # Merging URL arguments dict with new params
    #     parsed_get_args.update(params)
    #
    #     # Bool and Dict values should be converted to json-friendly values
    #     # you may throw this part away if you don't like it :)
    #     parsed_get_args.update(
    #         {k: dumps(v) for k, v in parsed_get_args.items()
    #          if isinstance(v, (bool, dict))}
    #     )
    #
    #     # Converting URL argument to proper query string
    #     encoded_get_args = urlencode(parsed_get_args, doseq=True)
    #     # Creating new parsed result object based on provided with new
    #     # URL arguments. Same thing happens inside of urlparse.
    #     new_url = ParseResult(
    #         parsed_url.scheme, parsed_url.netloc, parsed_url.path,
    #         parsed_url.params, encoded_get_args, parsed_url.fragment
    #     ).geturl()
    #
    #     return new_url

# For self running
if __name__ == '__main__':
    tm = TrelloManager()
    cards_array = tm.getListCards(Credentials().trello_in_progress_dev_list)
    print('Cards: ', cards_array)


