import discord
from discord.ext import commands
import requests
import time

class profile_requests:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {'X-Riot-Token': self.api_key}
        self.url = "https://na1.api.riotgames.com"

    def get_summonerid(self, summoner_name):
        url = f'{self.url}/lol/summoner/v4/summoners/by-name/{summoner_name}'
        resp = requests.get(url, headers=self.headers)
        return resp.json()

    def get_ranked_stats(self, summoner_id):
        url = f'{self.url}/lol/league/v4/entries/by-summoner/{summoner_id}'
        resp = requests.get(url, headers=self.headers)
        return resp.json()

    def get_profile_info(self, summoner_name):
        profile_info = self.get_summonerid(summoner_name)
        if ('id' in profile_info):
            league_info = self.get_ranked_stats(profile_info['id'])
            return [profile_info, league_info]
        elif 'status' in profile_info:
            return profile_info['status']['status_code']
        else:
            return None

    def get_match_info(self, summoner_name):
        """ Gets the active match information """
        summoner_id = self.get_summonerid(summoner_name)["id"]
        #Returns the 404 status if summoner is not found
        if 'status' in summoner_id:
            return summoner_id['status']['status_code']
        url = f'{self.url}/lol/spectator/v4/active-games/by-summoner/{summoner_id}'
        resp = requests.get(url, headers = self.headers).json()
        #Returns the error message if the request summoner is not in game
        if 'status' in resp:
            return resp['status']['status_code']
        #Returns the game information if the summoner is found & is in a game
        else:
            summ_ids = [player["summonerId"] for player in resp["participants"]]
            summ_names = [player["summonerName"] for player in resp["participants"]]
            time.sleep(0.25)
            levels = self.get_levels(*summ_names)
            # levels = []
            time.sleep(0.25)
            ranks = self.get_solo_ranks(*summ_ids)
            match_info = {
                "gameMode": resp["gameMode"],
                "mapId": resp["mapId"],
                "gameQueueConfigId": resp["gameQueueConfigId"],
                "gameLength": resp["gameLength"],
                "summoners": resp["participants"],
                "levels": levels,
                "ranks": ranks
            }
            return match_info

    def get_levels(self, *args):
        levels = []
        for name in args:
            sum_info = self.get_summonerid(name)
            levels.append(sum_info["summonerLevel"])
        return levels

    def get_solo_ranks(self, *args):
        player_ranks = []
        for summ_id in args:
            ranks = self.get_ranked_stats(summ_id)
            added = False
            for rank, index in zip(ranks, range(0,len(ranks))):
                if rank["queueType"] == "RANKED_SOLO_5x5":
                    player_ranks.append(rank)
                    added = True
            if not added:
                player_ranks.append({})
        return player_ranks