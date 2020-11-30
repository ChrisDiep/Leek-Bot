import discord
from discord.ext import commands
import requests


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
        league_info = self.get_ranked_stats(profile_info['id'])
        return [profile_info, league_info]

