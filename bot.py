import discord
from discord.ext import commands
import os
import re
import traceback
import datetime
from helpers.League.profile_helpers import APIKeyExpired
client = commands.Bot(command_prefix='!')
from safe import BOT


@client.event
async def on_ready():
    """ Indicates bot is ready and gets the application info """
    print('Bot is ready.')
    if not hasattr(client, 'appinfo'):
        client.appinfo = await client.application_info()


@client.event
async def on_error(event, *args, **kwargs):
    """ Sends a direct message to the me when there is an error thrown """
    embed = discord.Embed(title=':x: Event Error',
                          colour=0xe74c3c)  # Red
    embed.add_field(name='Event', value=event)
    embed.description = '```py\n%s\n```' % traceback.format_exc()
    embed.timestamp = datetime.datetime.utcnow()
    await client.appinfo.owner.send(embed=embed)


@client.event
async def on_command_error(ctx, error):
    """
    Checks for errors from discord.py and raises an error if
    the error is not specifically categorized here
    """
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.channel.send(f'{ctx.author.mention} Command on cooldown, please wait to try again')
    elif isinstance(error, commands.CommandNotFound):
        await ctx.channel.send(f'{ctx.author.mention} Command not found! Check your spelling')
    elif isinstance(error, commands.CommandInvokeError):
        if isinstance(error.original, APIKeyExpired):
            await client.appinfo.owner.send("API Key Expired")
            await ctx.channel.send(f'{ctx.author.mention} API Key expired, bot author messaged')
    else:
        await ctx.channel.send(f'{ctx.author.mention} Error! Issue sent to bot author')
        raise error


@client.command(name="ping", help="Replies with the bot latency")
@commands.cooldown(1, 1, commands.BucketType.default)
async def ping(ctx):
    """ Tests the response time of the bot """
    await ctx.send(f'{round(client.latency * 1000)} ms')

# @client.command(name="emoji")
# async def print_emoji(ctx):
#     emojis = discord.utils.get(client.emojis)
#     print(type(emojis))
#     emoji = discord.utils.get(client.emojis, name="diamond")
#     await ctx.send(f'{str(emoji)} here')

# @client.command(name="owner")
# async def print_owner(ctx):
#     await ctx.send(f'{client.appinfo.owner.mention} hello')


@client.event
async def on_message(message):
    if not message.guild:
        guild = client.get_guild(781361389679280168)
        channel = guild.get_channel(798413003187159080)
        await channel.send(f'{message.author}: {message.content}')
    await client.process_commands(message)

#Loads the cogs for the bot
for filename in os.listdir('./Cogs/League'):
    if filename.endswith('.py'):
        client.load_extension(f'Cogs.League.{filename[:-3]}')

client.run(BOT.get('TOKEN'))
# client.run(os.getenv("TOKEN", "optional-default"))

