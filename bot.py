import discord
from discord.ext import commands
from safe import BOT
import os

client = commands.Bot(command_prefix='!')


@client.event
async def on_ready():
    print('Bot is ready.')


@client.command(name="ping", help="Replies with the bot latency")
async def ping(ctx):
    await ctx.send(f'{round(client.latency * 1000)} ms')

for filename in os.listdir('./Cogs/League'):
  if filename.endswith('.py'):
    client.load_extension(f'Cogs.League.{filename[:-3]}')

client.run(BOT.get('TOKEN'))
