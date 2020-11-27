#!/usr/bin/env python
#
# Copyright 2016  Roanuz Softwares Private Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import requests
import logging
import os
import json
from datetime import datetime
from pyfootball_storagehandler import RfaStorageHandler

import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()


logger = logging.getLogger('RfaApp')
logger.setLevel(logging.ERROR)  # Now we handled INFO or ERROR level
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class RfaApp():
    """
    The RfaApp class will be containing various function to access
    the different FootballAPI API's.
    """

    def __init__(self, access_key=None, secret_key=None, app_id=None, store_handler=None, device_id=None):
        """ 
        initializing user Football API app details.
        Arg:
            access_key : Football API APP access_key
            secret_key : Football API APP secret_key
            store_handler : RfaStorageHandler/RfaFileStorageHandler object name
            device_id : User device_id

        """
        if access_key:
            self.access_key = access_key
        elif os.environ.get("RFA_ACCESS_KEY"):
            self.access_key = os.environ.get("RFA_ACCESS_KEY")
        else:
            raise Exception("access key is required.!! Try again")

        if secret_key:
            self.secret_key = secret_key
        elif os.environ.get("RFA_SECRET_KEY"):
            self.secret_key = os.environ.get("RFA_SECRET_KEY")
        else:
            raise Exception("secret key is required.!! Try again")

        if app_id:
            self.app_id = app_id
        elif os.environ.get("RFA_APP_ID"):
            self.app_id = os.environ.get("RFA_APP_ID")
        else:
            raise Exception("app id is required.!! try again")

        if store_handler:
            self.store_handler = store_handler
        else:
            self.store_handler = RfaStorageHandler()

        self.api_path = "https://api.footballapi.com/v1/"
        if device_id:
            new_id = device_id
        else:
            new_id = self.store_handler.new_device_id()
        self.store_handler.set_value("device_id", new_id)
        self.device_id = new_id
        self.auth()

    def auth(self):
        """
        Auth is used to call the AUTH API of FootballAPI.
       
        Access token required for every request call to FootballAPI.
        Auth functional will post user Football API app details to server
        and return the access token.

        Return:
            Access token
        """
        if not self.store_handler.has_value('access_token'):
            params = {}
            params["access_key"] = self.access_key
            params["secret_key"] = self.secret_key
            params["app_id"] = self.app_id
            params["device_id"] = self.device_id
            auth_url = self.api_path + "auth/"
            response = self.get_response(auth_url, params, "auth")

            if 'auth' in response:
                self.store_handler.set_value("access_token", response['auth']['access_token'])
                self.store_handler.set_value("expires", response['auth']['expires'])
                logger.info('Getting new access token')
            else:
                msg = "Error getting access_token, " + \
                      "please verify your access_key, secret_key and app_id"
                logger.error(msg)
                raise Exception("Auth Failed, please check your access details")

    def get_response(self, url, params={}, method="get"):
        """
        It will return json response based on given url, params and methods.
    
        Arg:    
           params: 'dictionary'
           url: 'url' format
           method: default 'get', support method 'post' 
        Return:
           json data
        """

        if method == "post":
            response_data = json.loads(requests.post(url, params=params).text)
        elif method == "auth":
            response_data = json.loads(requests.post(url, json=params).text)
        else:
            params["access_token"] = self.get_active_token()
            response_data = json.loads(requests.get(url, params=params).text)

        if not response_data['status_code'] == 200:
            if "status_msg" in response_data:
                logger.error("Bad response: " + response_data['status_msg'])
            else:
                logger.error("Some thing went wrong, please check your " + \
                             "request params Example: card_type and date")

        return response_data

    def get_active_token(self):
        """
        Getting the valid access token.

           Access token expires every 24 hours, It will expires then it will
           generate a new token.
        Return:
           active access token
        """

        expire_time = self.store_handler.has_value("expires")
        access_token = self.store_handler.has_value("access_token")
        if expire_time and access_token:
            expire_time = self.store_handler.get_value("expires")
            if not datetime.now() < datetime.fromtimestamp(float(expire_time)):
                self.store_handler.delete_value("access_token")
                self.store_handler.delete_value("expires")
                logger.info('Access token expired, going to get new token')
                self.auth()
            else:
                logger.info('Access token noy expired yet')
        else:
            self.auth()
        return self.store_handler.get_value("access_token")

    def get_match(self, match_key):
        """
        Calling match API

        Response:
        Match data
        """

        match_url = self.api_path + 'match/' + str(match_key) + '/'
        response = self.get_response(match_url)
        return response

    def get_tournament(self, tournament_key):
        """
        Calling tournament API

        Response:
        Tournament data
        """

        tournament_url = self.api_path + 'tournament/' + str(tournament_key) + '/'
        response = self.get_response(tournament_url)
        return response

    def get_tournament_team(self, tournament_key, team_key):
        """
        Calling tournament team API

        Response:
        Tournament team data
        """

        tournament_team_url = self.api_path + 'tournament/' + str(tournament_key) + '/team/' + str(team_key) + '/'
        response = self.get_response(tournament_team_url)
        return response

    def get_tournament_round(self, tournament_key, round_key):
        """
        Calling tournament round API

        Response:
        Tournament round data
        """

        tournament_round_url = self.api_path + 'tournament/' + str(tournament_key) + '/round-detail/' + str(round_key) + '/'
        response = self.get_response(tournament_round_url)
        return response

    def get_tournament_stats(self, tournament_key):
        """
        Calling Tournament Stats API

        Response:
        Stats of the Tournament
        """

        tournament_stats_url = self.api_path + 'tournament/' + str(tournament_key) + '/stats/'
        response = self.get_response(tournament_stats_url)
        return response

    def get_tournament_team_stats(self, tournament_key, team_key):
        """
        Calling Tournament Team Stats API
        
        Response:
        Stats of the team in that tournament
        """

        tournament_team_stats_url = (
            self.api_path + 'tournament/' + str(tournament_key) + '/team/' + str(team_key) + '/stats/')
        response = self.get_response(tournament_team_stats_url)
        return response

    def get_tournament_player_stats(self, tournament_key, player_key):
        """
        Calling Tournament Player Stats API

        Response:
        Stats of Player in that tournament
        """

        tournament_player_stats_url = (
            self.api_path + 'tournament/' + str(tournament_key) + '/player/' + str(player_key) + '/stats/')
        response = self.get_response(tournament_player_stats_url)
        return response

    def get_schedule(self, date=None):
        """
        Calling Schedule API

        Args:
            month: YYYY-MM

        Response:
        Schedule of the given month
        """
        params = {}
        if date:
            params['date'] = date

        schedule_url = self.api_path + 'schedule/'
        response = self.get_response(schedule_url, params)
        return response

    def get_tournament_schedule(self, tournament_key):
        """
        Calling Tournament Schedule API

        Response:
        Schedule of the tournament
        """

        tournament_schedule_url = self.api_path + 'tournament/' + str(tournament_key) + '/schedule'
        response = self.get_response(tournament_schedule_url)
        return response

    def get_recent_tournaments(self):
        """
        Calling Recent Tournaments API

        Response:
        Recent tournaments data
        """

        recent_tournament_url = self.api_path + 'recent_tournaments/'
        response = self.get_response(recent_tournament_url)
        return response

    def get_round_matches(self, tournament_key, round_key):
        """
        Calling Round matches API

        Response:
        Matches in the round
        """

        round_matches_url = self.api_path + 'tournament/' + str(tournament_key) + '/matches/' + str(round_key)
        response = self.get_response(round_matches_url)
        return response

    def get_recent_tournament_matches(self, tournament_key):
        """
        Calling Recent Tournament Matches API

        Response:
        Recent matches in the tournament
        """

        recent_tournament_matches_url = self.api_path + 'tournament/' + str(tournament_key) + '/matches/'
        response = self.get_response(recent_tournament_matches_url)
        return response

    def get_tournament_standings(self, tournament_key):
        """
        Calling Tournament Standings API

        Response:
        Tournament points table
        """

        tournament_standings_url = self.api_path + 'tournament/' + str(tournament_key) + '/standings/'
        response = self.get_response(tournament_standings_url)
        return response

    def get_fantasy_match_credits(self, match_key, model="RZ-C-A100"):
        """
        Calling Fantasy Match Credits API

        Args:
            model_key: Credits Model Key
            Default model_key is RZ-C-A100

        Response:
        Fantasy Credits of the Induvidual Players in the Match Squad
        """
        params = {
            "model": model
        }

        fantasy_match_credits_url = self.api_path + 'fantasy-match-credits/' + str(match_key) + '/'
        response = self.get_response(fantasy_match_credits_url, params=params)
        return response

    def get_fantasy_match_points(self, match_key, model="RZ-C-A100"):
        """
        Calling Fantasy Match Points API

        Args:
            model_key: Points Model Key
            Default model_key is RZ-C-A100

        Response:
        Fantasy Match Points of the Induvidual Players in the Match Squad
        """
        params = {
            "model": model
        }

        fantasy_match_points_url = self.api_path + 'fantasy-match-points/' + str(match_key) + '/'
        response = self.get_response(fantasy_match_points_url, params=params)
        return response
