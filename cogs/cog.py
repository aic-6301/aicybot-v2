import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import locale_str


class cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name='ping', description="BotのPingを取得します")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("Pong!:ping_pong: {0}ms".format(round(self.bot.latency * 1000)), ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(cog(bot))