import discord
from discord.ext import commands
from discord import app_commands

from utils import osu as osuapi


class osu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    group = app_commands.Group(name="osu", description="osu!関連のコマンド")
    
    @group.command(name="user", description="ユーザーの情報を取得します")
    @app_commands.describe(user='ユーザー名')
    async def user(self, interaction: discord.Interaction, user: str):
        if user.isdigit():
            user = int(user)
        else:
            user = '@'+user
        try:
            data = osuapi.get_user(user)
            embed = discord.Embed(title=f"{data['username']}の情報", color=discord.Color.dark_gold())
            embed.set_thumbnail(url=data['avatar_url'])
            embed.add_field(name="PP", value=f"{data['statistics']['pp']:.0f}")
            embed.add_field(name="国内ランキング / 世界ランキング", value=f"#{str(data['statistics']['country_rank'])} / #{(data['statistics']['global_rank'])}")
            embed.add_field(name="レベル", value=data['statistics']['level']['current'])
            embed.add_field(name="精度", value=f"{data['statistics']['hit_accuracy']:.2f}%")
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            print(data)
            await interaction.response.send_message(f"エラーが発生しました。\n```{e}```", ephemeral=True)
        
    

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(osu(bot))