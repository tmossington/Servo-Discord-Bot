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
from uszipcode import SearchEngine

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

# Greet and Goodbye Messages
@bot.event
async def on_message(message):

    print(f'Message from {message.author.name}({message.channel.guild}, {message.channel.name}): {message.content}')

    username = str(message.author).split("#")[0]
    channel = str(message.channel.name)
    user_message = str(message.content)

    if message.author == bot.user:
        return    
    
    message_content = user_message.lower()
    if "hi" in message_content.split() or 'hello' in message_content.split():
        await message.channel.send(f"Hello {username}")
    
    elif "bye" in message_content.split() or "goodbye" in message_content.split():
        await message.channel.send(f"Goodbye {username}")


    await bot.process_commands(message)

# Random Number Generator
@bot.command()
async def number(ctx):
    random_num = random.uniform(0, 10**10)

    await ctx.send(f"Random number: {random_num}")


#Weather Command
@bot.command()
async def weather(ctx, *, location):
    
    # Check if the input is a valid zip code
    search = SearchEngine()
    zipcode_data = search.by_zipcode(location)

    if zipcode_data:
        # If a valid zip code, use it directly
        city = zipcode_data.major_city
        state = zipcode_data.state
        location = f"{city}"
    else:
        # If not a valid zip code, use the input as a city name
        location = location
        state = ""
    
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
        weather_list = data['weather']
        weather_info = weather_list[0]
        conditions = weather_info['description']
        
        
        # Add name and country to the weather data
        name = data['name']
        sys = data['sys']
        country = sys['country']
    
    # Send weather data in discord chat
    if state:
        await ctx.send(f"{name}, {state}, {country}: {temp}°F, {conditions}")
    else:
        await ctx.send(f"{name}, {country}: {temp}°F, {conditions}")
        


bot.run(TOKEN)
