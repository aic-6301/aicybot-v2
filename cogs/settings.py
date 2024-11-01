import discord
from discord.ext import commands
from discord import app_commands

from utils import database


class settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    server = app_commands.Group(name='server', description='サーバーに関するコマンドです')
    
    @server.command(name='expand', description='メッセージを自動で展開するか設定します。')
    @app_commands.describe(mode='展開するかどうかを設定します。')
    @app_commands.choices(mode=[
        app_commands.Choice(name="展開する", value=1),
        app_commands.Choice(name="展開しない", value=0)
    ])
    @app_commands.default_permissions(manage_guild=True)
    async def expand(self, interaction: discord.Interaction, mode: int):
        database.set('expand', 'bool', mode, interaction.guild.id)
        await interaction.response.send_message(f'メッセージの展開を{"有効" if mode else "無効"}にしました。', ephemeral=True)
    
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(settings(bot))