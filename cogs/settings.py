import discord
from discord.ext import commands
from discord import app_commands

from utils import database


class settings(commands.Cog):
    bot: commands.Bot
    
    def __init__(self, bot):
        self.bot = bot

    settings = app_commands.Group(name = 'settings', description = 'サーバー設定に関するコマンドです')
    
    @settings.command(name = 'expand', description = 'メッセージを自動で展開するか設定します。')
    @app_commands.describe(mode = '展開するかどうかを設定します。')
    @app_commands.choices(mode = [
        app_commands.Choice(name = "展開する", value = 1),
        app_commands.Choice(name = "展開しない", value = 0)
    ])
    @app_commands.default_permissions(manage_guild = True)
    async def expand(self, interaction: discord.Interaction, mode: int):
        print(mode)
        if database.get('settings', interaction.guild.id) is None:
            database.insert('settings', ['guild', 'expand'], [interaction.guild.id, mode])
        else:
            database.update('settings', ['expand'], [mode], key_value = interaction.guild.id)
        await interaction.response.send_message(f'メッセージの展開を{"有効" if mode else "無効"}にしました。', ephemeral = True)
    
    @settings.command(name = 'log', description = 'ログを設定します。')
    @app_commands.describe(mode = 'ログを有効にするかどうかを設定します。', channel = 'ログを送信するチャンネルを設定します。')
    @app_commands.choices(mode = [
        app_commands.Choice(name = "有効", value = 1),
        app_commands.Choice(name = "無効", value = 0)
    ])
    @app_commands.default_permissions(manage_guild = True)
    async def log(self, interaction: discord.Interaction, mode: int, channel: discord.TextChannel = None):
        if mode and not channel:
            await interaction.response.send_message('ログチャンネルが設定されていません。', ephemeral = True)
            return
        
        try:
            if database.get('settings', interaction.guild.id) is None:
                database.insert('settings', ['guild', 'log_ch'], [interaction.guild.id, channel.id])
            else:
                database.update('settings', ['log_ch'], [channel.id], key_value = interaction.guild.id)
            await interaction.response.send_message(f'ログを{f"有効にし、{channel.mention}にログチャンネルを設定" if mode else "無効に"}しました。\n-# ※適用まで時間がかかる可能性があります。', ephemeral = True)
        except Exception as e:
            await interaction.response.send_message(f'エラーが発生しました: `{e}`', ephemeral = True)
            

    
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(settings(bot))
