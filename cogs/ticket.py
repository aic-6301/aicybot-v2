import discord
from discord.ext import commands
from discord import app_commands


class ticket(commands.Cog):
    bot: commands.Bot

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='ticket', description="チケットを作成します")
    async def ticket(self, interaction: discord.Interaction):
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name="チケット")
        if category is None:
            category = await guild.create_category("チケット")
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True)
        }
        channel = await category.create_text_channel(f"ticket-{interaction.user.display_name}", overwrites=overwrites)
        await channel.send("チケットを作成しました。")
        await interaction.response.send_message("チケットを作成しました。", ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ticket(bot))