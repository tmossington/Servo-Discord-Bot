import os
import discord
from dotenv import load_dotenv
import random
from discord.ext import commands
from discord import app_commands
from discord.ext.commands import Bot
#import interactions
from discord import Intents
import config
import random
import requests
from uszipcode import SearchEngine
import wordle
import randomanswer
import asyncio
import wordle_db as db
import datetime
import capital_game
import re
from discord.ext import tasks


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')


intents = discord.Intents.all()

intents.members = True

help_command = commands.DefaultHelpCommand(
    no_category = 'Commands'
)

bot = commands.Bot(command_prefix = '/', intents=intents, help_command = help_command)



connection, cursor = db.connect_to_db()
message_sent = False

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord')
    morning_report.start()

    for guild in bot.guilds:
        #if guild.name == GUILD:
         #   break
        print(f'{guild.name}(id: {guild.id})')
    
        members = '\n - '.join([member.name for member in guild.members])
        print(f'Guild Members:\n - {members}')
        print(guild.text_channels)

        # Announce new features
        global message_sent
        channel = discord.utils.get(guild.text_channels, id=883484321804091415)
        if channel and not message_sent:
            message = "Hello! I'd like to announce some new features that have been added:\n\n" \
                        "**Help function**: Use /help to see a list of all available bot commands.\n" \
                        "**Wordle User Statistics**: User stats for the daily wordle game will now be tracked. Use /stats to see your personal stats."
            await channel.send(message)
            message_sent = True

            with open('announcement_status.txt', 'w') as f:
                f.write('message_sent')
        elif message_sent:
            print("Message already sent")
        else:
            print("Channel not found")
try:
    with open('announcement_status.txt', 'r') as f:
        status = f.read()
        if status == 'message_sent':
            message_sent = True
except FileNotFoundError:
    pass

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
        
    global daily_game_active
    if isinstance(message.channel, discord.DMChannel) and message.author != bot.user and daily_game_active:
        game = games.get(message.channel.id)
        if game is None:
            await message.channel.send("There's no active game. Start a new game with /wordle_day")
            return
        
        guess = message.content
        response = game.send_guess(guess)
        await message.channel.send(response)
        if game.is_over():
            daily_game_active = False
            games.pop(message.channel.id)
            # Update user stats
            user_id = str(message.author.id)
            username = str(message.author)
            db.update_user_stats(connection, cursor, user_id, username, game.guessed_correctly, game.guesses_made)


    await bot.process_commands(message)

# Random Number Generator
@bot.command(help="Generates a random number between 0 and 10^10")
async def number(ctx):
    random_num = random.uniform(0, 10**10)

    await ctx.send(f"Random number: {random_num}")

async def fetch_weather(location):
    # Check if the input is a valid zip code
    search = SearchEngine()
    zipcode_data = search.by_zipcode(location)

    if zipcode_data:
        # If a valid zip code, use it directly
        city = zipcode_data.major_city
        state = zipcode_data.state
        location = location + ',us'
    else:
        # If not a valid zip code, use the input as a city name
        location = location + ',us'
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
    
    return f"{name}, {state}, {country}: {temp}°F, {conditions}" 

#Weather Command
@bot.command(help="Returns the current weather for a specified location")
async def weather(ctx, *, location):
    weather_report = await fetch_weather(location)
    await ctx.send(weather_report)

# Financial Report using Tiingo API
@bot.command(help="Returns the current price of a stock symbol")
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


@bot.command(help="Returns the current price of a cryptocurrency")
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
games = {}
@bot.command(help="Play a game of wordle. Guess the word in 6 tries or less.")
async def wordle(ctx, guess: str):
    #global game
    import wordle
    game = games.get(ctx.channel.id)
    if game is None:
        await ctx.send("There's no active game. Start a new game with /new_wordle")
        return
    
    response = game.send_guess(guess.lower())

    # Check if the game is over
    if "The game is over" in response or "You have run out of guesses" in response:
        # Remove game from the games dictionary
        del games[ctx.channel.id]
    print(response)
    await ctx.send(response)

@bot.command(help="Starts a new game of wordle")
async def new_wordle(ctx):
    import wordle
    #global game
    game = wordle.Wordle(word=randomanswer.random_word(), real_word=True)
    games[ctx.channel.id] = game
    await ctx.send("New game started! Guess away with /wordle.")


daily_game_active = False

@bot.command(help="Play the wordle of the day. Guess the word in 6 tries or less.")
async def wordle_day(ctx):
    member = ctx.author
    #global game
    global daily_game_active
    import wordle
    word = randomanswer.daily_random_word()
    game = wordle.Wordle(word=word, real_word=True)
    daily_game_active = True

    if ctx.guild is None: # The command was sent in a DM
        await ctx.send("New game started! Type your guess below.")
        games[ctx.channel.id] = game
    else: # The command was sent in a server
        await member.create_dm()
        games[member.dm_channel.id] = game
        await member.dm_channel.send("New game started! Type your guess below.")

    # Check if game is won
    guessed_correctly = game.guessed_correctly
    if guessed_correctly == True:
        game_won = True
    else:
        game_won = False

    
    
@bot.command(help="Returns user stats for the daily wordle game")
async def stats(ctx, user=None):
    rows = None
    if user is None:
        user_id = ctx.author.id
        rows = db.get_user_stats(cursor, user_id=user_id)
    elif re.match('<@\d+>', user):
        user_id = int(re.sub('\D', '', user)) # If the user argument is a mention
        print(user_id)
        rows = db.get_user_stats(cursor, user_id=user_id)
    elif user.isdigit():
        rows = db.get_user_stats(cursor, user_id=int(user)) # If the user argument is a user ID
    else:
        rows = db.get_user_stats(cursor, username=user) # If the user argument is a username

    if not rows:
        await ctx.send("No stats found.")
    else:
        first_row = rows[0]
        username = first_row[1]
        games_played = sum(row[2] for row in rows if row[2] is not None)
        games_won = sum(row[3] for row in rows if row[3] is not None)
        games_lost = sum(row[4] for row in rows if row[4] is not None)
        total_guesses = sum(row[5] for row in rows if row[5] is not None)
        average_guesses_per_game = sum(row[6] for row in rows if row[6] is not None)
        await ctx.send(f"Username: {username}, Games played: {games_played}, Games won: {games_won}, Games lost: {games_lost}, Guesses made: {total_guesses}, Average guesses per game: {average_guesses_per_game}, Win rate: {games_won/games_played:.2f}")



@bot.command(help="Returns the list of all user stats for the daily wordle game")
async def stat_report(ctx):
    cursor.execute('SELECT * FROM user_stats')
    rows = cursor.fetchall()
    for row in rows:
        user_id, username, games_played, games_won, games_lost, total_guesses, average_guesses_per_game, last_played = row
        await ctx.send(f"Username: {username}, Games played: {games_played}, Games won: {games_won}, Games lost: {games_lost}, Total guesses: {total_guesses}, Average guesses per game: {average_guesses_per_game}")

@bot.command(help="Play a game of guessing the capital of a country")
async def capital(ctx):
    country = random.choice(list(capital_game.country_capitals.keys()))
    capital = capital_game.country_capitals[country]
    await ctx.send(f"What is the capital of {country}?")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        guess = await bot.wait_for('message', check=check, timeout=60.0)
    except asyncio.TimeoutError:
        await ctx.send(f"Time's up! The correct answer was {capital}")
    else:
        if guess.content.lower() == capital.lower():
            await ctx.send("Correct!")
        else:
            await ctx.send(f"Wrong! The correct answer was {capital}")

@bot.command()
async def announce(ctx, *, message):
    channel = bot.get_channel(883484321804091415)
    await channel.send(message)



### NYT API
async def fetch_nyt(ctx):
    NYT_API_KEY = os.getenv('NYT_API')
    url = f'https://api.nytimes.com/svc/topstories/v2/home.json?api-key={NYT_API_KEY}'
    response = requests.get(url)
    data = response.json()
    
    top_stories = data['results'][:5]

    stories_text = ""
    for story in top_stories:
        title = story['title']
        url = story['url']
        stories_text += f"{title}: <{url}>\n"
    return stories_text



@tasks.loop(minutes=1.0)
async def morning_report():
    # Verify correct time to report
    if datetime.datetime.now().hour == 8 and datetime.datetime.now().minute == 0:
        # Perform all data collection jobs for the report
        # Get the channel to send the report
        channel = bot.get_channel(883484321804091415)
        # Get the weather report for Arlington, VA and Warren, MI
        weather_report_VA = await fetch_weather('22201')
        weather_report_MI = await fetch_weather('48089')

        # News report
        headlines = await fetch_nyt(channel)

        await channel.send(f"Good morning! Here is the morning report: \n\nWeather: \n"
                        f"Arlington, VA: {weather_report_VA}\n"
                        f"Warren, MI: {weather_report_MI}\n\n"
                        f"Top News Headlines: \n{headlines}\n\n"

                        f"Have a great day!")

bot.run(TOKEN)
