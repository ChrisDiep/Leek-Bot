import discord
from discord.ext import commands
from safe import BOT
import os
import re
import traceback
import datetime
client = commands.Bot(command_prefix='!')


@client.event
async def on_ready():
    print('Bot is ready.')
    if not hasattr(client, 'appinfo'):
        client.appinfo = await client.application_info()


@client.event
async def on_error(event, *args, **kwargs):
    embed = discord.Embed(title=':x: Event Error',
                          colour=0xe74c3c)  # Red
    embed.add_field(name='Event', value=event)
    embed.description = '```py\n%s\n```' % traceback.format_exc()
    embed.timestamp = datetime.datetime.utcnow()
    await client.appinfo.owner.send(embed=embed)


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.channel.send(f'{ctx.author.mention} Command on cooldown, try again')
    elif isinstance(error, commands.CommandNotFound):
        await ctx.channel.send(f'{ctx.author.mention} Command not found! Check your spelling')
    else:
        await ctx.channel.send(f'{ctx.author.mention} Error! Issue sent to bot author')
        raise error


@client.command(name="ping", help="Replies with the bot latency")
@commands.cooldown(1, 1, commands.BucketType.default)
async def ping(ctx):
    await ctx.send(f'{round(client.latency * 1000)} ms')

for filename in os.listdir('./Cogs/League'):
    if filename.endswith('.py'):
        client.load_extension(f'Cogs.League.{filename[:-3]}')

# @client.command(name="test")
# async def test(ctx, *args):
#     parsed = ''.join(map(lambda word: re.sub(r'[^a-zA-Z0-9]','',word), args))
#     await ctx.send(parsed)

client.run(BOT.get('TOKEN'))
