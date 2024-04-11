# levels.py
# Started 04/08/2024

## File for XP and leveling system for SERVO.

import discord
from discord.ext import commands
import random
import mysql.connector
from mysql.connector import Error


# Componenets:

# 1. XP system
# 2. Leveling system
# 3. Leaderboard
# 4. Level up messages
 

# XP system

# Given for messages sent in the server, voice calls, command use, XP mulitipliers for different times, role-based rewards

# Leveling system
class LevelingSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_xp = {}
        self.user_level = {}
        self.connection, self.cursor = self.connect_to_db()

    def connect_to_db(self):
        # Connect to MySQL Database
        connection = None
        cursor = None
        try:
            connection = mysql.connector.connect(
                host = host,
                user = root,
                password = password,
                database = database
            )

            if connection.is_connected():
                db_info = connection.get_server_info()
                print("Connect to MySQL Serer version ", db_info)

                cursor = connection.cursor()
                cursor.execute("CREATE DATABASE IF NOT EXISTS rank_system")
                connection.commit() # Commit the new database

                connection.database = "rank_system"
                cursor.execute("CREATE TABLE IF NOT EXISTS user_levels (user_id VARCHAR(255), username VARCHAR(255), level INT DEFAULT 1, xp INT DEFAULT 0, PRIMARY KEY (user_id))")
                connection.commit() # commit the new table
        except Error as e:
            print("Error while connecting to MySQL", e)
        
        return connection, cursor

    async def update_user_stats(self, user_id, username, xp, level):
        try:
            self.cursor.execute("INSERT INTO user_levels (user_id, username, xp, level) VALUES (%s, %s, %s, %S) "
                                "ON DUPLICATE KEY UPDATE xp = %s, level = %s",
                                (user_id, username, xp, level, xp, level))
            self.connection.commit()
        except Error as e:
            print("Error while update MySQL", e)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.guild is None or message.guild.id != 1059619615950516334: #### REMOVE BEFORE DEPLOYMENT
            return
        
        user_id = message.author.id
        username = str(message.author)

        # Fetch user's current level and XP from database
        self.cursor.execute("SELECT username, level, xp FROM user_levels WHERE user_id = %s", (user_id,))
        result = self.cursor.fetchone()
        if result:
            username, level, xp = result
        else:
            # If user doesn't exist in database, initialize their level and XP
            level = 1
            xp = 0
            self.cursor.execute("INSERT INTO user_levels (user_id, username, level, xp) VALUES (%s, %s, %s, %s)",
                                (user_id, username, level, xp))
            self.connection.commit()

        # Give user random XP between 1 and 9
        xp += random.randint(10, 25)

        # Level up user when they reach enough XP
        if xp >= level**2 * 100:
            level += 1
            await message.channel.send(f"Congrats {message.author.mention}! You have leveled up to level {level}!")

        # Update the database with new level and XP
        self.cursor.execute("UPDATE user_levels SET level = %s, xp = %s WHERE user_id = %s",
                            (level, xp, user_id))
        self.connection.commit()



    @commands.command()
    async def level(self, ctx, member: discord.Member = None):
        if ctx.guild is None or ctx.guild.id != 1059619615950516334: ### REMOVE BEFORE DEPLOYMENT
            return
        member = member or ctx.author
        user_id = member.id
        
        # Fetch user's level from database
        self.cursor.execute("SELECT level FROM user_levels WHERE user_id = %s", (user_id,))
        result = self.cursor.fetchone()
        if result:
            level = result[0]
        else:
            level = 1 # Default level if user hasn't been added to database yet


        await ctx.send(f'{member.mention} is at level {level}!')

    @commands.command()
    async def leaderboard(self, ctx, limit: str = '10'):
        if ctx.guild is None or ctx.guild.id != 1059619615950516334: ### REMOVE BEFORE DEPLOYMENT
            return
        
        # Fetch top 10 user's levels from database
        if limit.lower() == 'all':
            self.cursor.execute('SELECT * FROM user_levels ORDER BY level DESC, xp DESC')
        else:
            self.cursor.execute('SELECT * FROM user_levels ORDER BY level DESC, xp DESC LIMIT %s', (int(limit),))
        rows = self.cursor.fetchall()
        for row in rows:
            user_id, username, level, xp = row
            await ctx.send(f"Username: **{username}**, Level: {level}")

    
    # Reset user levels
    @commands.command()
    async def reset(self, ctx, member: discord.Member):
        if ctx.guild is None or ctx.guild.id != 1059619615950516334: ### REMOVE BEFORE DEPLOYMENT
            return
        
        member = member or ctx.author
        user_id = member.id

        # Reset user's level in database
        level = 1
        xp = 0
        self.cursor.execute("UPDATE user_levels SET level = %s, xp = %s WHERE user_id = %s",
                            (level, xp, user_id))
        self.connection.commit()
        # send message
        await ctx.send(f"{member.mention} levels reset")

    # Give level
    @commands.command()
    async def levelup(self, ctx, levels: int, member:discord.Member = None):
        if ctx.guild is None or ctx.guild.id != 1059619615950516334: ### REMOVE BEFORE DEPLOYMENT
            return
        
        member = member or ctx.author
        user_id = member.id


        # Fetch user's current level
        self.cursor.execute("SELECT level FROM user_levels WHERE user_id = %s", (user_id,))
        result = self.cursor.fetchone()
        if result:
            level = result[0]
        else:
            level = 1

        level += levels
        xp = 0
        
        # Update the database with new level and XP
        self.cursor.execute("UPDATE user_levels SET level = %s, xp = %s WHERE user_id = %s",
                            (level, xp, user_id))
        self.connection.commit()

        if levels == 1:
            await ctx.send(f"{levels} level added to {member.mention}.")
        else:
            await ctx.send(f"{levels} levels added to {member.mention}.")





        

async def setup(bot):
    await bot.add_cog(LevelingSystem(bot))