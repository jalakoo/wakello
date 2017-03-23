#!/usr/bin/env python

import hashlib
import os
import sys
from rauth import OAuth2Service

if sys.version_info[0] == 3:
  raw_input = input

class WakatimeOAuth(object):

    def authenticate(self, client_id, secret):
        # client_id = raw_input('Enter your App Id: ')
        # secret = raw_input('Enter your App Secret: ')

        service = OAuth2Service(
            client_id=client_id, # your App ID from https://wakatime.com/apps
            client_secret=secret, # your App Secret from https://wakatime.com/apps
            name='Wakello',
            authorize_url='https://wakatime.com/oauth/authorize',
            access_token_url='https://wakatime.com/oauth/token',
            base_url='https://wakatime.com/api/v1/')

        redirect_uri = 'https://wakatime.com/oauth/test'
        state = hashlib.sha1(os.urandom(40)).hexdigest()
        params = {'scope': 'email,read_logged_time',
                  'response_type': 'code',
                  'state': state,
                  'redirect_uri': redirect_uri}

        url = service.get_authorize_url(**params)

        print('**** Visit {url} in your browser. ****'.format(url=url))
        print('**** After clicking Authorize, paste code here and press Enter ****')
        code = raw_input('Enter code from url: ')

        # the code should be returned upon the redirect from the authorize step,
        # be sure to use it here (hint: it's in the URL!)
        # also, make sure returned state has not changed for security reasons.
        headers = {'Accept': 'application/x-www-form-urlencoded'}
        session = service.get_auth_session(headers=headers,
                                           data={'code': code,
                                                 'grant_type': 'authorization_code',
                                                 'redirect_uri': redirect_uri})

        print(session.get('users/current').json()['data']['email'])
