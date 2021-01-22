import datetime
import json
from Requests.League.profiles import profile_requests
from helpers.League.profile_helpers import clean_input, get_version, get_champions, write_queue_ids, APIKeyExpired
import discord
from discord.ext import commands
import sys
from bot import client
sys.path.append('/home/chris/Documents/VSCode/SideProjects/FVHSBot/')
import os
from safe import BOT


class LeagueProfiles(commands.Cog):
    def __init__(self, client):
        self.client = client
        # self.request = profile_requests(BOT.get("API_KEY"))
        self.request = profile_requests(os.getenv("API_KEY", "optional-default"))
        self.version = get_version()
        self.champion_ids = get_champions(self.version)
        self.queue_ids = write_queue_ids()

    @commands.command(name="Rank", help="Prints out ranks of the user, limited to 20 Requests per 120 seconds", aliases=['rank'])
    @commands.cooldown(20, 120, commands.BucketType.default)
    async def print_ranked_stats(self, ctx, *name):
        parsed_name = clean_input(name)
        profile_info = self.request.get_profile_info(parsed_name)
        if isinstance(profile_info, list):
            summonerIconID = profile_info[0]['profileIconId']
            profile_info[1] = self._fill_blanks(profile_info[1])
            ranks_info = list(map(self._extract_ranks, profile_info[1]))
            await ctx.send(f'{ctx.author.mention}', embed=self._build_ranked_embed(profile_info[0]['name'], summonerIconID, ranks_info))
        elif profile_info == 404:
            await ctx.send(f'{ctx.author.mention} Error, Summoner not found!')
        elif profile_info == 403:
            raise commands.CommandInvokeError(APIKeyExpired())

    @commands.command(name="Match", help="Prints out match information, limited to 4 Requests per 120 Seconds", aliases=["m", "match"])
    @commands.cooldown(4, 120, commands.BucketType.default)
    async def print_match_info(self, ctx, *summoner_name):
        resp = self.request.get_match_info(clean_input(summoner_name))
        # resp = get_match_info(summoner_name)
        # resp = json.load(open("dummy2.json"))
        if isinstance(resp, dict):
            embed_info = {
                "gameMode": resp["gameMode"],
                "mapId": resp["mapId"],
                "gameLength": resp["gameLength"],
                "gameQueueConfigId": resp["gameQueueConfigId"],
                "summoners": [],
                "levels": resp["levels"],
                "ranks": []
            }
            # f = open("dummy.json")
            # profile_info = json.load(f)
            # f1 = open("dummy_profiles.json")
            # ranks = json.load(f1)
            # embed_info["gameMode"] = profile_info["gameMode"]
            # embed_info["mapId"] = profile_info["mapId"]
            # embed_info["gameLength"] = profile_info["gameLength"]
            # embed_info["gameQueueConfigId"] = profile_info["gameQueueConfigId"]
            for summoner, index in zip(resp["summoners"], range(0, len(resp["summoners"]))):
                emoji_summoner = discord.utils.get(
                    client.emojis, name=self.champion_ids[str(summoner["championId"])])
                emoji_rank = emoji_rank = discord.utils.get(
                    client.emojis, name='unranked')
                tier = "Unranked"
                rank = ""
                lp = ""
                wrapped_lp = ""
                if "tier" in resp["ranks"][index]:
                    emoji_rank = discord.utils.get(
                        client.emojis, name=resp["ranks"][index]["tier"].lower())
                    tier = resp["ranks"][index]["tier"]
                    rank = resp["ranks"][index]["rank"]
                    lp = str(resp["ranks"][index]["leaguePoints"])
                    wrapped_lp = f'({lp} LP)'
                embed_info["summoners"].append(
                    f'{str(emoji_summoner)} {summoner["summonerName"]}')
                embed_info["ranks"].append(
                    f'{str(emoji_rank)} {tier.title()} {rank} {wrapped_lp}'
                )
            await ctx.send(f'{ctx.author.mention}', embed=self._build_match_embed(embed_info))
        elif resp == 400:
            await ctx.send(f'{ctx.author.mention} Error, Summoner not found!')
        elif resp == 404:
            await ctx.send(f'{ctx.author.mention}, {" ".join(summoner_name)} doesn\'t appear to be in a game')
        elif resp == 403:
            raise commands.CommandInvokeError(APIKeyExpired(ctx.message.author))

    def _build_match_embed(self, info):
        # info["levels"] = ["2", "3", "4", "5",
        #                   "54", "520", "213", "123", "12", "123"]
        half_num_summoners = int(len(info["summoners"])/2) - 1
        info["summoners"][half_num_summoners] = f"{info['summoners'][half_num_summoners]}\n"
        info["ranks"][half_num_summoners] = f"{info['ranks'][half_num_summoners]}\n"
        info["levels"][half_num_summoners] = f"{info['levels'][half_num_summoners]}\n"
        summoners = '\n'.join(info["summoners"])
        levels = [str(i).center(5, ' ') for i in info["levels"]]
        levels = '\n'.join(levels)
        ranks = '\n'.join(info["ranks"])
        game_time = f'{int(info["gameLength"]/60)}:{info["gameLength"]%60}'
        queue_info = self.queue_ids[info["gameQueueConfigId"]]
        title = queue_info["description"] if queue_info["description"] is not None else "Custom"
        embed = discord.Embed(
            title=f'{title} | {game_time}')
        embed.add_field(name="Summoner", value=summoners, inline=True)
        embed.add_field(name="Rank", value=ranks, inline=True)
        embed.add_field(name="Level", value=levels, inline=True)
        embed.set_footer(
            text=f'Questions or Suggestions? Message {client.appinfo.owner.display_name} or DM the bot itself')
        return embed

    def _extract_ranks(self, league):
        tier = league['tier'].lower().capitalize()
        queue_type = league['queueType'].replace('_', ' ').title()
        rank_info = {
            'queue_type': queue_type,
            'tier': tier,
            'rank': league['rank'],
            'wins': league['wins'],
            'league_points': league['leaguePoints'],
            'losses': league['losses']
        }
        return rank_info

    def _build_ranked_embed(self, name, icon, ranks):
        embed = discord.Embed(color=0x00ff00)
        embed.set_author(
            name=name, icon_url=f"http://ddragon.leagueoflegends.com/cdn/{self.version}/img/profileicon/{icon}.png")
        embed.set_thumbnail(url=self._get_highest_rank(ranks)["image"])
        for queue in ranks:
            embed.add_field(
                name=queue['queue_type'],
                value=f'Rank: {queue["tier"]} {queue["rank"]} \n W/L: {queue["wins"]}/{queue["losses"]} \n LP: {queue["league_points"]}',
                inline=True
            )
        embed.set_footer(
            text=f'Questions or Suggestions? Message {client.appinfo.owner.display_name} or DM the bot itself')
        return embed

    def _get_highest_rank(self, ranks):
        ranksDict = {
            "unranked": [-1, 'https://static.wikia.nocookie.net/leagueoflegends/images/3/38/Season_2019_-_Unranked.png'],
            "iron": [0, 'https://fvhs-bot.s3-us-west-1.amazonaws.com/Emblem_Iron.png'],
            "bronze": [1, 'https://fvhs-bot.s3-us-west-1.amazonaws.com/Emblem_Bronze.png'],
            "silver": [2, 'https://fvhs-bot.s3-us-west-1.amazonaws.com/Emblem_Silver.png'],
            "gold": [3, 'https://fvhs-bot.s3-us-west-1.amazonaws.com/Emblem_Gold.png'],
            "platinum": [4, 'https://fvhs-bot.s3-us-west-1.amazonaws.com/Emblem_Platinum.png'],
            "diamond": [5, 'https://fvhs-bot.s3-us-west-1.amazonaws.com/Emblem_Diamond.png'],
            "master": [6, 'https://fvhs-bot.s3-us-west-1.amazonaws.com/Emblem_Master.png'],
            "grandmaster": [7, 'https://fvhs-bot.s3-us-west-1.amazonaws.com/Emblem_Grandmaster.png'],
            "challenger": [8, 'https://fvhs-bot.s3-us-west-1.amazonaws.com/Emblem_Challenger.png']
        }
        highest_rank = ""
        for rank in ranks:
            current_rank = ranksDict[rank['tier'].lower()]
            if highest_rank == "":
                highest_rank = current_rank
            else:
                if (highest_rank[0] < current_rank[0]):
                    highest_rank = current_rank
        # return highest_rank[1]
        return {
            "image": highest_rank[1],
            "rank": highest_rank,
        }

    def _fill_blanks(self, ranks):
        new_ranks = ranks
        blank_flex = {
            'queueType': 'Ranked Flex Sr',
            'tier': 'unranked',
            'rank': '',
            'wins': '~',
            'leaguePoints': 'N/A',
            'losses': '~'
        }
        blank_solo = {
            'queueType': 'Ranked Solo 5x5',
            'tier': 'unranked',
            'rank': '',
            'wins': '~',
            'leaguePoints': 'N/A',
            'losses': '~'
        }
        if (len(new_ranks) == 0):
            new_ranks.append(blank_flex)
            new_ranks.append(blank_solo)
        elif (len(new_ranks) == 1):
            if (new_ranks[0]['queueType'] == 'RANKED_SOLO_5x5'):
                new_ranks.append(blank_flex)
            else:
                new_ranks.append(blank_solo)
        return new_ranks


def setup(client):
    client.add_cog(LeagueProfiles(client))
