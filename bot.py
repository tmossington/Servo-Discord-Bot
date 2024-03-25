import os
import discord
from dotenv import load_dotenv
import random
from discord.ext import commands
from discord import app_commands
from discord.ext.commands import Bot
import interactions
from discord import Intents
import config
import random
import requests

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.all()

intents.members = True

bot = commands.Bot(command_prefix = '/', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord')
    for guild in bot.guilds:
        #if guild.name == GUILD:
         #   break
        print(f'{guild.name}(id: {guild.id})')
    
        members = '\n - '.join([member.name for member in guild.members])
        print(f'Guild Members:\n - {members}')




@bot.event
async def on_message(message):

    print(f'Message from {message.author.name}({message.channel.guild}, {message.channel.name}): {message.content}')

    username = str(message.author).split("#")[0]
    channel = str(message.channel.name)
    user_message = str(message.content)

    if message.author == bot.user:
        return    
    hello_phrases_to_check = ["hello", "hi"]
    bye_phrases_to_check = ["goodbye", "bye"]

    if any(phrase in user_message.lower() for phrase in hello_phrases_to_check):
        await message.channel.send(f"Hello {username}")
    
    elif any(phrase in user_message.lower() for phrase in bye_phrases_to_check):
        await message.channel.send(f"Goodbye {username}")
   
    await bot.process_commands(message)


@bot.command()
async def number(ctx):
    random_num = random.uniform(0, 10**10)

    await ctx.send(f"Random number: {random_num}")

#Weather Command
@bot.command()
async def weather(ctx, *, location):
    WeatherAPI_Key  = '9f7181e1f2bfd3070530d4b905ed5ef8'
    url = f'https://api.openweathermap.org/data/2.5/weather?q={location}&appid={WeatherAPI_Key}&units=imperial'
    # Fetch weather data from the API
    response = requests.get(url)
    data = response.json()
    # print data to console for easier debugging
    print(data)

    # Check if location is valid
    if 'message' in data:
        error_message = data['message']
        await ctx.send(f"Error: {error_message}")
        return
    
    # Extract weather information
    for weather_data in data:
        weather = data['main']
        temp = weather['temp']
        name = data['name']
        sys = data['sys']
        country = sys['country']
    
    # Send weather data in discord chat
    await ctx.send(f"{name}, {country}: {temp}°F")
        


bot.run(TOKEN)
