# Steam cog

import requests
import json
from dotenv import load_dotenv
import os
import discord
from discord.ext import commands
import aiohttp

class SteamStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = os.getenv('Steam_APIKey')

    @commands.command()
    async def get_appid(self, game_name):
        response = requests.get('http://api.steampowered.com/ISteamApps/GetAppList/v2/')
        data = response.json()

        for app in data['applist']['apps']:
            if app['name'] ==game_name:
                print(app['appid'])
                return app['appid']

        # If not found, return none
        return None        

    @commands.command()
    async def steam_user_stats(self, ctx, user_id: str, game_id: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(f'http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid={game_id}&key={self.api_key}&steamid={user_id}') as response:
                user_stats = await response.json()  # parse the response as JSON
            
            relevant_info = {
                
            }

    # Now you can do something with user_stats, like send it to the user
        await ctx.send(user_stats)


async def setup(bot):
    await bot.add_cog(SteamStats(bot))


