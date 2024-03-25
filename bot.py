import os
import discord
from dotenv import load_dotenv
import random
from discord.ext import commands
from discord import app_commands
import interactions
from discord import Intents
import config
from random import choice

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.all()

client = discord.Client(intents = intents)

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break
    print(
        f'{client.user} has connected to Discord'
        f'{guild.name}(id: {guild.id})'
    )
    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')

@client.event
async def on_message(message):
    username = str(message.author).split("#")[0]
    channel = str(message.channel.name)
    user_message = str(message.content)

    if message.author == client.user:
        return
    
    if user_message.lower() == "hello" or "hi":
        await message.channel.send(f"Hello {username}")
        return

client.run(TOKEN)