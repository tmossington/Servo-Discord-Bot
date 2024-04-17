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

from datetime import datetime, timedelta
import capital_game
import re
from discord.ext import tasks
from github import Github
import banned_words
import pytz



load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')


intents = discord.Intents.all()

intents.members = True

help_command = commands.DefaultHelpCommand(
    no_category = 'Commands'
)

bot = commands.Bot(command_prefix = '/', intents=intents, help_command = help_command)

bot.load_extension('Cog.LevelingSystem')
bot.load_extension('Cog.SteamStats')

#bot.load_extension=('levels')

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

    await bot.load_extension('LevelingSystem')
    print('LevelingSystem cog loaded')
    await bot.load_extension('SteamStats')
    print('SteamStats cog loaded')


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

        


    #Get incorrect letters
        guessed_letters_not_in_word = response[3] if len(response) > 3 else None

            # Parse the response based on its type
        if isinstance(response, tuple):
            # Get the number of guesses left and the guessed letters not in the word
            guesses_left = response[2] if len(response) > 2 else None
            guessed_letters_not_in_word = response[3] if len(response) > 3 else None
            response_string = response[0]
        else:
            # The response is a string
            guesses_left = None
            guessed_letters_not_in_word = None
            response_string = response

        # Create the embed
        embed = discord.Embed(
            title=f"Wordle! \n{guesses_left} guesses left" if guesses_left else "Wordle!",
            description = response_string,
            color=discord.Color.dark_green()
            )
        
        # Add guessed_letters_not_in_word to embed
        if guessed_letters_not_in_word:
            embed.add_field(name="Incorrect letters:", value=guessed_letters_not_in_word, inline=False)

        #await ctx.send(response)
        await message.channel.send(embed=embed)




        #await message.channel.send(response)
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
    embed = discord.Embed(
        title=f"Random number:",
        description=random_num,
        color=discord.Color.red()
    )

    await ctx.send(embed=embed)

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
    
    WeatherAPI_Key  = os.getenv('WeatherAPI_Key')
    url = f'https://api.openweathermap.org/data/2.5/weather?q={location}&appid={WeatherAPI_Key}&units=imperial'



    # Fetch weather data from the API
    response = requests.get(url)
    data = response.json()
    # print data to console for easier debugging
    print(data)

    # Check if location is valid
    if 'message' in data:
        error_message = data['message']
        return error_message
    
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
    embed = discord.Embed(
        title=f"Current Weather for {location}",
        description=weather_report,
        color= discord.Color.blue()

    )

    await ctx.send(embed=embed)

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
            # Make embed
            embed = discord.Embed(
                title=f"Current price for {symbol}",
                description=f"${price}",
                color=discord.Color.gold()
            )
            await ctx.send(embed=embed)

     # if it's a dictionary, get the relevant information
    elif isinstance(data, dict):
        price = data.get('last')
        symbol = data.get('ticker')

        # Make embed
        embed = discord.Embed(
            title=f"Current price for {symbol}",
            description=f"${price}",
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)

    # if it's neither, send an error message
    else:
        await ctx.send("Invalid response format.")


@bot.command(help="Returns current crypto price. Symbol given must include currency (BTCUSD, not BTC for bitcoin in USD).")
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

                    # Make embed:
                    embed = discord.Embed(
                        title=f"Current price for {symbol}",
                        description=f"${price}",
                        color=discord.Color.dark_gold()
                    )
                    await ctx.send(embed=embed)
            else:
                price = topOfBookData.get('lastPrice')
                embed = discord.Embed(
                    title=f"Current price for {symbol}",
                    description=f"${price}",
                    color=discord.Color.dark_gold()
                    )
                await ctx.send(embed=embed)

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

    # Parse the response based on its type
    if isinstance(response, tuple):
        # Get the number of guesses left and the guessed letters not in the word
        guesses_left = response[2] if len(response) > 2 else None
        guessed_letters_not_in_word = response[3] if len(response) > 3 else None
        response_string = response[0]
    else:
        # The response is a string
        guesses_left = None
        guessed_letters_not_in_word = None
        response_string = response

    # Create the embed
    embed = discord.Embed(
        title=f"Wordle! \n{guesses_left} guesses left" if guesses_left else "Wordle!",
        description = response_string,
        color=discord.Color.dark_green()
        )
    
    # Add guessed_letters_not_in_word to embed
    if guessed_letters_not_in_word:
        embed.add_field(name="Incorrect letters:", value=guessed_letters_not_in_word, inline=False)

    #await ctx.send(response)
    await ctx.send(embed=embed)

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
        rows = db.get_user_stats(connection, cursor, user_id=user_id)
    elif re.match('<@\d+>', user):
        user_id = int(re.sub('\D', '', user)) # If the user argument is a mention
        print(user_id)
        rows = db.get_user_stats(connection, cursor, user_id=user_id)
    elif user.isdigit():
        rows = db.get_user_stats(connection, cursor, user_id=int(user)) # If the user argument is a user ID
    else:
        rows = db.get_user_stats(connection, cursor, username=user) # If the user argument is a username

    if not rows:
        await ctx.send("No stats found.")
    else:
        first_row = rows[0]
        username = first_row[1]
        games_played = sum(row[2] for row in rows if row[2] is not None)
        total_guesses = sum(row[3] for row in rows if row[3] is not None)
        games_won = sum(row[4] for row in rows if row[4] is not None)
        games_lost = sum(row[5] for row in rows if row[5] is not None)
        average_guesses_per_game = sum(row[6] for row in rows if row[6] is not None)

        # Create the embed
        embed = discord.Embed(
            title=f"Wordle_day stats for {username}",
            color=discord.Color.dark_green()
        )

        # Add fields to the embed
        embed.add_field(name="Games played", value=games_played, inline=False)
        embed.add_field(name="Games won", value=games_won, inline=False)
        embed.add_field(name="Games lost", value=games_lost, inline=False)
        embed.add_field(name="Guesses made", value=total_guesses, inline=False)
        embed.add_field(name="Average guesses per game", value=average_guesses_per_game, inline=False)
        embed.add_field(name="Win rate", value=f"{games_won/games_played:.2f}", inline=False)

        await ctx.send(embed=embed)
        #await ctx.send(f"Username: **{username}**, Games played: {games_played}, Games won: {games_won}, Games lost: {games_lost}, Guesses made: {total_guesses}, Average guesses per game: {average_guesses_per_game}, Win rate: {games_won/games_played:.2f}")



@bot.command(help="Returns the list of all user stats for the daily wordle game")
async def stat_report(ctx):
    cursor.execute('SELECT * FROM user_stats')
    rows = cursor.fetchall()

    embed = discord.Embed(
        title=f"Stat Report for Wordle_Day",
        color=discord.Color.dark_green()
    )
    for row in rows:
        user_id, username, games_played, total_guesses, games_won, games_lost, average_guesses_per_game, last_played = row

        message = (f"Username: **{username}**, Games played: {games_played}, Games won: {games_won}, Games lost: {games_lost}, Total guesses: {total_guesses}, Average guesses per game: {average_guesses_per_game}")
        
        embed.description = embed.description + "\n\n" + message if embed.description else message

    # Send the embed to the channel
    await ctx.send(embed=embed)

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
    my_id = os.getenv('discord_id')
    if str(ctx.author.id) != my_id:
        await ctx.send("You do not have permission to use this command.")
        return
    channel = bot.get_channel(883484321804091415)

    # Create an embed for the announcement
    embed = discord.Embed(
        title = ":loudspeaker: Announcement",
        description=message,
        color=discord.Color.gold()
    )
    

    await channel.send(embed=embed)

ticket_ids = {}
ticket_creators = {}
@bot.command(help="Submit a bug report or suggestion for the bot")
async def ticket(ctx, *, message):
    channel = bot.get_channel(1228026400989118464)
    ticket_id = random.randint(1000, 9999)

    while ticket_id in ticket_ids:
        ticket_id = random.randit(1000, 9999)

 

    # Create embed for the ticket
    embed = discord.Embed(
        title=f"Ticket-{ticket_id}",
        description=message,
        color=discord.Color.dark_purple()
    )

# Check if the author has an avatar
    if ctx.author.avatar:
        avatar_url = ctx.author.avatar.url
    else:
        avatar_url = 'https://example.com/default_avatar.png'

    embed.set_author(name=ctx.author.display_name, icon_url=avatar_url)
    embed.set_footer(text=f"Ticket created by {ctx.author.display_name}")

    # Send the embed to the channel
    sent_message = await channel.send(embed=embed)

    # Store ticket
    ticket_ids[ticket_id] = sent_message.id
    ticket_creators[ticket_id] = str(ctx.author.id)

    # Notify user
    await ctx.send(f"Your ticket has been submitted. The ticket ID is {ticket_id}")

@bot.command(help="Close a ticket")
async def ticket_close(ctx, ticket_id: int):
    my_id = os.getenv('discord_id')
    creator_id = ticket_creators.get(ticket_id)

    if str(ctx.author.id) != my_id and str(ctx.author.id) != creator_id:
        await ctx.send("You do not have permission to use this command.")
        return
    
    channel = bot.get_channel(1228026400989118464)

    # Get message ID from ticket ID
    message_id = ticket_ids.get(ticket_id)
    if not message_id:
        await ctx.send(f"Ticket {ticket_id} does not exist.")
        return

    # Get the message by the ID
    message = await channel.fetch_message(message_id)

    # delete the message
    await message.delete()

    # Remove ticket ID from dict
    del ticket_ids[ticket_id]

    # Notify the user
    await ctx.send(f"Ticket {ticket_id} has been closed.")




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
    eastern = pytz.timezone('US/Eastern')
    current_time = datetime.now(eastern)
    current_date = datetime.now().date()
    day_of_week = current_date.strftime('%A')

    if current_time.hour == 8 and current_time.minute == 0:
        # Perform all data collection jobs for the report
        # Get the channel to send the report
        channel = bot.get_channel(883484321804091415)
        # Get the weather report for Arlington, VA and Warren, MI
        weather_report_VA = await fetch_weather('22201')
        weather_report_MI = await fetch_weather('48089')

        # News report
        headlines = await fetch_nyt(channel)

        message = (f"Good morning! Here is the morning report: \n\n **Weather:** \n Arlington, VA: {weather_report_VA}\n Warren, MI: {weather_report_MI}\n\n **Top News Headlines:** \n{headlines}\n\n Have a great day!")


        embed = discord.Embed(
        title=f"Morning Report for {day_of_week}, {current_date}",
        description=message,
        color=discord.Color.blue()
    )
    
        await channel.send(embed=embed)
        

                        
        
@bot.command()
async def reload_cog(ctx, *, cog: str):
    my_id = os.getenv('discord_id')
    if str(ctx.author.id) != my_id:
        await ctx.send("You do not have permission to use this command.")
        return
    try:
        bot.unload_extension(f"cogs.{cog}")
        bot.load_extension(f"cogs.{cog}")
    except Exception as e:
        await ctx.send(f"**`ERROR:`** {type(e).__name__} - {e}")
    else:
        await ctx.send(f"**`SUCCESS:`** {cog} has been reloaded")

bot.run(TOKEN)
