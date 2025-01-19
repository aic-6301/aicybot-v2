import discord
from discord.ext import commands
from discord import app_commands

from utils import database

class server(commands.Cog):
    bot: commands.Bot
    
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild
        if member.bot:
            data = database.get('join_bot', guild.id)
            if data is not None and data[1]:
                data = database.get('join_bot', guild.id)
                role = guild.get_role(data[3])
                if not role:
                    return
                await member.add_roles(role)
                if data[4]:
                    channel = guild.get_channel(data[4])
                    embed = discord.Embed(title=f"Botの{member.name}が参加しました！", color=discord.Color.green())
                    embed.add_field(name="参加日時", value=f"{discord.utils.format_dt(member.joined_at, 'T')}", inline=False)
                    embed.add_field(name="アカウント作成日", value=f"{discord.utils.format_dt(member.created_at, 'T')}", inline=False)
                    embed.add_field(name="現在のサーバー人数", value=f"{guild.member_count}人", inline=False)
                    embed.set_thumbnail(url=member.avatar.url)
                    await channel.send(embed=embed)
                    return
        else:        
            if database.get('join', guild.id)[1]:
                channel = guild.get_channel(database.get('join', guild.id)[1])
                if not channel:
                    return
                embed = discord.Embed(title=f"{member.name}が参加しました！", color=discord.Color.green())
                embed.add_field(name="参加日時", value=f"{discord.utils.format_dt(member.joined_at, 'T')}", inline=False)
                embed.add_field(name="アカウント作成日", value=f"{discord.utils.format_dt(member.created_at, 'T')}", inline=False)
                embed.add_field(name="現在のサーバー人数", value=f"{guild.member_count}人", inline=False)
                embed.set_thumbnail(url=member.avatar.url)
                await channel.send(embed=embed)
                return
            
        

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(server(bot))