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
import wordle
import randomanswer
import asyncio

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
        print(guild.text_channels)

# Welcome Message
@bot.event
async def on_member_join(member):
    default_channel = discord.utils.get(member.guild.text_channels, name="the-boston-tea-party")
    await default_channel.send(f"Welcome {member.mention} to the server!")

    channel = discord.utils.get(member.guild.text_channels)
    print(channel)


# Greet and Goodbye Messages
@bot.event
async def on_message(message):


    username = str(message.author).split("#")[0]

    if message.guild:
        print(f'Message from {message.author.name}({message.channel.guild}, {message.channel.name}): {message.content}')

        channel = str(message.channel.name)
    else:
        print(f'Message from', {message.author.name}, " in DM: ", message.content)
        channel = "Direct Message"
    user_message = str(message.content)

    if message.author == bot.user:
        return    
    
    message_content = user_message.lower()
    if "hi" in message_content.split() or 'hello' in message_content.split():
        await message.channel.send(f"Hello {username}")
    
    elif "bye" in message_content.split() or "goodbye" in message_content.split():
        await message.channel.send(f"Goodbye {username}")


    ### Block of response for wordle_day command
        
    global game
    global daily_game_active
    if isinstance(message.channel, discord.DMChannel) and message.author != bot.user and daily_game_active:
        guess = message.content
        response = game.send_guess(guess)
        await message.channel.send(response)
        if game.is_over():
            daily_game_active = False


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
        

# Financial Report using Tiingo API
@bot.command()
async def price(ctx, *, symbol):
    stockAPI_Key = os.getenv('tiingo_API')
    url = f'https://api.tiingo.com/iex/{symbol}?token={stockAPI_Key}'

    headers = {
            'Content-Type': 'application/json'
            }
    requestResponse = requests.get(url,headers=headers)
    print(requestResponse.json())
    data = requestResponse.json()

    if len(data) == 0:
        await ctx.send("Invalid symbol")
        return
    

    # Check if the response is a list or dictionary

    # if it's a list, handle each element individually
    if isinstance(data, list):
        for item in data:
            price = item.get('last')
            symbol = item.get('ticker')
            await ctx.send(f"{symbol}: ${price}")

     # if it's a dictionary, get the relevant information
    elif isinstance(data, dict):
        price = data.get('last')
        symbol = data.get('ticker')
        await ctx.send(f"{symbol}: ${price}")

    # if it's neither, send an error message
    else:
        await ctx.send("Invalid response format.")


@bot.command()
async def crypto(ctx, *, symbol):
    stockAPI_Key = os.getenv('tiingo_API')
    #url = f'https://api.tiingo.com/tiingo/crypto/prices?tickers={symbol}&token={stockAPI_Key}'
    url = f'https://api.tiingo.com/tiingo/crypto/top?tickers={symbol}&token={stockAPI_Key}'

    headers = {
            'Content-Type': 'application/json'
            }
    requestResponse = requests.get(url,headers=headers)
    data = requestResponse.json()

    # Verify if the symbol is valid
    if len(data) == 0:
        await ctx.send("Invalid symbol")
        return
    
    # Check if the response is a list or dictionary

    # if it's a list, handle each element individually
    if isinstance(data, list):
        for item in data:
            symbol = item.get('ticker')
            topOfBookData = item.get('topOfBookData')
            # check if topOfBookData is a list or dict
            if isinstance(topOfBookData, list):
                for book_data in topOfBookData:
                    price = book_data.get('lastPrice')
                    await ctx.send(f"{symbol}: ${price}")
            else:
                price = topOfBookData.get('lastPrice')
                await ctx.send(f"{symbol}: ${price}")

     # if it's a dictionary, get the relevant information
    elif isinstance(data, dict):
        symbol = data.get('ticker')
        topOfBookData = data.get('topOfBookData')
        if isinstance(topOfBookData, list):
            for book_data in topOfBookData:
                price = book_data.get('lastPrice')
                await ctx.send(f"{symbol}: ${price}")
        else:
            price = topOfBookData.get('lastPrice')
            await ctx.send(f"{symbol}: ${price}")

    # if it's neither, send an error message
    else:
        await ctx.send("Invalid response format.")


game = None

@bot.command()
async def wordle(ctx, guess: str):
    global game
    import wordle
    if game is None:
        await ctx.send("There's no active game. Start a new game with /new_wordle")
        return
    
    response = game.send_guess(guess.lower())
    await ctx.send(response)

@bot.command()
async def new_wordle(ctx):
    import wordle
    global game
    game = wordle.Wordle(word=randomanswer.random_answer(), real_word=True)
    await ctx.send("New game started! Guess away with /wordle.")


daily_game_active = False

@bot.command()
async def wordle_day(ctx):
    member = ctx.author
    global game
    global daily_game_active
    import wordle
    word = randomanswer.random_answer()
    game = wordle.Wordle(word=word, real_word=True)
    daily_game_active = True

    if ctx.guild is None: # The command was sent in a DM
        await ctx.send("New game started! Type your guess below.")
    else: # The command was sent in a server
        await member.create_dm()
        await member.dm_channel.send("New game started! Type your guess below.")
    


bot.run(TOKEN)
