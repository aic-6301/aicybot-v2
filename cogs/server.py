import discord
from discord.ext import commands
from discord import app_commands

from utils import database

class server(commands.Cog):
    bot: commands.Bot
    
    def __init__(self, bot):
        self.bot = bot
    
    # TODO:そのうちサーバー情報とかを表示するコマンドを追加する
        

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(server(bot))