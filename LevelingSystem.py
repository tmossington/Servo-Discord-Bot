# levels.py
# Started 04/08/2024

## File for XP and leveling system for SERVO.

import discord
from discord.ext import commands
import random
import mysql.connector
from mysql.connector import Error
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from easy_pil import Canvas, Editor, Font, load_image_async, Text
import os
import json
from dotenv import load_dotenv

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


    host = os.getenv('host')
    user = os.getenv('user')
    password = os.getenv('password')
    database = os.getenv('database_level')
    load_dotenv()

    json_str = os.getenv('role_dict')
    role_dict_str = json.loads(json_str)
  
    # Convert keys to int
    role_dict = {int(k): v for k, v in role_dict_str.items()}

    def connect_to_db(self):
        # Connect to MySQL Database
        connection = None
        cursor = None
        try:
            connection = mysql.connector.connect(
                host = self.host,
                user = self.user,
                password = self.password,
                database = self.database
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

        # Give user random XP between 10 and 50
        xp += random.randint(10, 50)

        # Update the database with new XP
        self.cursor.execute("UPDATE user_levels SET xp = %s WHERE user_id = %s", (xp, user_id))
        self.connection.commit()

        # Fetch updated xp
        self.cursor.execute("SELECT xp FROM user_levels WHERE user_id = %s", (user_id,))
        result = self.cursor.fetchone()
        if result:
            xp = result[0]

        # Level up user when they reach enough XP
        if xp >= level**2 * 100:
            level += 1
            xp = 0

            # Update the database with new level and XP
            self.cursor.execute("UPDATE user_levels SET level = %s, xp = %s WHERE user_id = %s",
                                (level, xp, user_id))
            self.connection.commit()
        
            ## Assign roles
            self.cursor.execute("SELECT level FROM user_levels WHERE user_id = %s", (user_id,))
            result = self.cursor.fetchone()
            if result:
                level = result[0]

            new_role_name = None
            # Check if user's new level is in the dictionary:
            if level in self.role_dict:
                old_level = int(level) - 1
                if old_level in self.role_dict:
                    # Remove old row
                    old_role = discord.utils.get(message.author.roles, name = self.role_dict[old_level])
                    if old_role:
                        await message.author.remove_roles(old_role)
                
                # Assign new role
                guild = message.guild
                roles = await guild.fetch_roles()
                role = discord.utils.get(roles, name=self.role_dict[level])
                if role and role not in message.author.roles:
                    await message.author.add_roles(role)
                elif not role:
                    # Role doesn't exist
                    role = await guild.create_role(name=self.role_dict[level])
                    await message.author.add_roles(role)
                    new_role_name = role.name

            # Send level up message
            if new_role_name:
                await message.channel.send(f"Congrats {message.author.mention}! You have leveled up to level {level} and earned the role {new_role_name}!")
            else:
                await message.channel.send(f"Congrats {message.author.mention}! You have leveled up to level {level}!")


                



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


    async def get_user_info(self, user_id):
        # Fetch user's current level and XP from database
        self.cursor.execute("SELECT level, xp FROM user_levels WHERE user_id = %s", (user_id,))
        result = self.cursor.fetchone()
        if result:
            level, xp = result
        else:
            # If user doesn't exist in database, initialize their level and XP
            level = 1
            xp = 0

        # Calculate XP needed for next level
        xp_needed = level**2 * 100

        # Calculate rank (this is just an example, replace it with your actual rank calculation)
        rank = 1

        return {
            'level': level,
            'xp': xp,
            'xp_needed': xp_needed,
            'rank': rank
        }

    async def create_profile_card(self, user, user_info):
        canvas = Canvas((500, 200))

        # Level dictionary with image names
        image_dict= {
            range(1, 5): '1.jpg',
            range(5, 9): '2.jpg',
            range(10, 14): '3.jpg',
            range(15, 19): '4.jpg',
            range(20, 29): '5.jpg',
            range(30, 39): '6.jpg',
            range(40, 49): '7.jpg',
            range(50, 59): '8.jpg',
            range(60, 69): '9.jpg',
            range(70, 79): '10.jpg',
            range(80, 89): '11.jpg',
            range(90, 99): '12.jpg',
            range(100, 119): '13.jpg',
            range(120, 139): '14.jpg',
            range(140, 159): '15.jpg',
            range(160, 179): '16.jpg',
            range(180, 199): '17.jpg',
            range(200, 500): '18.jpg'
        }

        #Find the image file name for the user's level
        for level_range, file_name in image_dict.items():
            if user_info["level"] in level_range:
                image_file = file_name
                break
        else:
            image_file = 'default.jpg'

        

        # Load background image
        background = Image.open(f'/Users/tmossington/Projects/profile_images/{image_file}')
        background = background.resize((500, 200))

        filter = Image.new('RGBA', background.size, (0, 0, 0, 128))

        background.paste(filter, (0, 0), filter)

        draw = ImageDraw.Draw(background)


        # Load user avatar
        response = requests.get(user.avatar.url)
        avatar = Image.open(BytesIO(response.content))
        avatar = avatar.resize((80, 80))

        # Create mask image
        mask = Image.new('L', avatar.size, 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0) + avatar.size, fill=255)

        avatar.putalpha(mask)

        # paste avatar onto canvas
        background.paste(avatar, (20, 20), avatar)

        # Load Arial font with specific size
        font = ImageFont.truetype("Arial.ttf", 15)


        # Draw user level, xp, and rank
        draw.text((120, 30), user.name, font=font)
        draw.text((120, 60), f"Level: {user_info['level']}", font=font)
        draw.text((120, 90), f"XP: {user_info['xp']}/{user_info['xp_needed']}", font=font)
        draw.text((120, 120), f"Rank: {user_info['rank']}", font=font)

        # Draw progress bar for XP
        user_info['xp'] = max(min(user_info['xp'], user_info['xp_needed']), 0)
        progress = user_info['xp'] / user_info['xp_needed']
        draw.rounded_rectangle((120, 150, 420, 170), radius=10, fill="gray") # Gray background with rounded corners
        draw.rounded_rectangle((120, 150, 120 + 300 * progress, 170), radius=10, fill=(50, 162, 168))

        # Save image
        background.save('profile_card.png')

    @commands.command()
    async def profile(self, ctx, user: discord.User = None):
        if user is None:
            user = ctx.author  # If no user is mentioned, use the author of the message

    
         # Get the user's level, experience, and rank from the database
        user_info = await self.get_user_info(user.id)

        await self.create_profile_card(user, user_info)

        await ctx.send(file=discord.File('profile_card.png'))




async def setup(bot):
    await bot.add_cog(LevelingSystem(bot))