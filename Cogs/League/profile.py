from safe import BOT
from Requests.League.profiles import profile_requests
from helpers.League.profile_helpers import clean_input
import discord
from discord.ext import commands
import sys
sys.path.append('/home/chris/Documents/VSCode/SideProjects/FVHSBot/')


class LeagueProfiles(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.request = profile_requests(BOT.get("API_KEY"))

    @commands.command(name="GetRank", help="Prints out ranks of the user", aliases=['getrank'])
    @commands.cooldown(1, 1, commands.BucketType.default)
    async def print_ranked_stats(self, ctx, *name):
        parsed_name = clean_input(name)
        profile_info = self.request.get_profile_info(parsed_name)
        if (profile_info[1] == '404'):
            await ctx.send(f'{ctx.author.mention} Error, Summoner not found!')
        else:
            summonerIconID = profile_info[0]['profileIconId']
            profile_info[1] = self._fill_blanks(profile_info[1])
            ranks_info = list(map(self._extract_ranks, profile_info[1]))
            await ctx.send(embed=self._build_ranked_embed(profile_info[0]['name'], summonerIconID, ranks_info))

    def _extract_ranks(self, league):
        tier = league['tier'].lower().capitalize()
        words = league['queueType'].split('_')
        queueType = []
        for word in words:
            queueType.append(word.capitalize())
        rank_info = {
            'queue_type': " ".join(queueType),
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
            name=name, icon_url=f"http://ddragon.leagueoflegends.com/cdn/10.18.1/img/profileicon/{icon}.png")
        embed.set_thumbnail(url=self._get_highest_rank(ranks))
        for queue in ranks:
            embed.add_field(
                name=queue['queue_type'],
                value=f'Rank: {queue["tier"]} {queue["rank"]} \n W/L: {queue["wins"]}/{queue["losses"]} \n LP: {queue["league_points"]}',
                inline=True
            )
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
        return highest_rank[1]

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
