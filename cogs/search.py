import discord
from discord.ext import commands
from discord import app_commands

import os
import googlesearch
import Paginator
import typing

class search(commands.Cog):
    bot: commands.Bot
    
    def __init__(self, bot):
        self.bot = bot
    
    search = app_commands.Group(name = 'search', description = '検索に関するコマンドです')
    
    @search.command(name = 'google', description = 'Googleで検索します。')
    @app_commands.describe(query = '検索する内容', count = '検索結果の数')
    async def google(self, interaction: discord.Interaction, query: str, count: int = None):
        embeds = []
        embed = discord.Embed(title = f"{query}の検索結果", color = discord.Color.blurple())
        value = ""
        if count is None: count = 3
        try:
            for result in googlesearch.search(query, num_results = count, lang = 'jp', advanced = True):
                embed.add_field(name = result.title, value = f"{result.description}\n[見てみる]({result.url})", inline = False)
                embeds.append(embed)
                embed = discord.Embed(title = f"{query}の検索結果", color = discord.Color.blurple())
            if len(embed.fields) > 0:
                embeds.append(embed)
            
            if len(embeds) == 1:
                await interaction.response.send_message(embed=embeds[0])
            else:
                await Paginator.Simple().start(interaction, embeds)
        except Exception as e:
            await interaction.response.send_message(f"エラーが発生しました: {e}", ephemeral=True)
    
    @search.command(name = 'member', description = 'メンバーを検索します。')
    @app_commands.describe(member='検索するメンバー')
    async def member(self, interaction: discord.Interaction, member: discord.Member):
        member = interaction.guild.get_member(member.id)
        status = self.get_status(member.desktop_status or member.mobile_status or member.web_status)
        
        embed = discord.Embed(title = f"{member.name}の情報", color = discord.Color.blurple())
        embed.add_field(name = "名前",          value = member.name)
        embed.add_field(name = "ディスプレイ名", value = member.display_name)
        embed.add_field(name = "ニックネーム",   value = member.nick)
        embed.add_field(name = "ユーザーID",     value = member.id, inline = False)
        embed.add_field(name = "ステータス",     value = status)
        if member.activity:
            if isinstance(member.activity, discord.Spotify):
                desc = f'🎶{member.activity.name} \n(/playingで詳細を取得できます！)'
            elif isinstance(member.activity, discord.ActivityType.listening):
                desc = f'🎶{member.activity.name}\n (一部のプラットフォームでは`/playing`を対応しています！)'
            elif isinstance(member.activity, discord.Game):
                desc = f'{member.activity.name}\n{discord.utils.format_dt(member.activity.start)}～' 
            else:
                desc = member.activity.name
            embed.add_field(name = "プレイ中のアクティビティ", value = desc , inline = False)
        embed.add_field(name = "アカウント作成日", value = f"{discord.utils.format_dt(member.created_at, 'f')}")
        embed.add_field(name = "サーバー参加日時", value = f"{discord.utils.format_dt(member.joined_at, 'f')}")
        embed.set_thumbnail(url = member.avatar.url)
        await interaction.response.send_message(embed = embed, ephemeral = True)        
    
    def get_status(self, status: discord.Status):
        if status == discord.Status.online:
            return "<:online:1238112276125454407>オンライン"
        elif status == discord.Status.idle:
            return "<:idle:1238112282240614531>退席中"
        elif status == discord.Status.dnd or status == discord.Status.do_not_disturb:
            return "<:dnd:1238112290906177607>取り込み中"
        elif status == discord.Status.offline:
            return "<:offline:1238112283775729764>オフライン"
        else:
            return "不明"
        


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(search(bot))