# levels.py

## File for XP and leveling system for SERVO.

import discord
from discord.ext import commands
import random


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

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.guild is None:
            return
        
        if message.author.id not in self.user_xp:
            self.user_xp[message.author.id] = 0
            self.user_level[message.author.id] = 0

        user_id = message.author.id
        xp = self.user_xp.get(user_id, 0)
        level = self.user_level.get(user_id, 1)

        # Give user random XP between 10 and 20
        self.user_xp[user_id] = xp + random.randint(10, 20)

        # Level up user if they have enough XP
        if self.user_level >= level**2 * 100:
            self.user_level[user_id] = level + 1
            await message.channel.send(f"Congrats {message.author.mention}! You have leveled up to level {level + 1}!")

    @commands.command(name= 'level')
    async def level(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        user_id = member.id
        level = self.user_level.get(user_id, 1)
        

def setup(bot):
    bot.add_cog(LevelingSystem(bot))