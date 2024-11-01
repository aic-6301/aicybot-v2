import discord
from discord.ext import commands
from discord import app_commands

import os
import googlesearch
import Paginator

class search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    search = app_commands.Group(name='search', description='検索に関するコマンドです')
    
    @search.command(name='google', description='Googleで検索します。')
    @app_commands.describe(query='検索する内容', count='検索結果の数')
    async def google(self, interaction: discord.Interaction, query: str, count: int = None):
        embeds = []
        embed = discord.Embed(title=f"{query}の検索結果", color=discord.Color.blurple())
        value = ""
        if count is None: count = 3
        try:
            for i, result in enumerate(googlesearch.search(query, num_results=count, lang='jp', advanced=True)):
                embed.add_field(name=result.title, value=f"{result.description}\n[見てみる]({result.url})", inline=False)
                embeds.append(embed)
                embed = discord.Embed(title=f"{query}の検索結果", color=discord.Color.blurple())
            if len(embed.fields) > 0:
                embeds.append(embed)
            
            if len(embeds) == 1:
                await interaction.response.send_message(embed=embeds[0])
            else:
                await Paginator.Simple().start(interaction, embeds)
        except Exception as e:
            await interaction.response.send_message(f"エラーが発生しました: {e}", ephemeral=True)
        

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(search(bot))