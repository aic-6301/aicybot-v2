import discord
from discord.ext import commands
from discord import app_commands

from utils import database

class server(commands.Cog):
    bot: commands.Bot
    
    def __init__(self, bot):
        self.bot = bot
    
    # TODO:そのうちサーバー情報とかを表示するコマンドを追加する
    
    @app_commands.command(name='server', description='サーバー情報を表示します。')
    @app_commands.describe(server='サーバーIDを指定します。')
    async def server(self, interaction: discord.Interaction, server: int = None):
        if server is None:
            server = interaction.guild.id
        guild = self.bot.get_guild(server)
        if guild is None:
            await interaction.response.send_message('サーバーが見つかりませんでした。', ephemeral=True)
            return
        embed = discord.Embed(title=guild.name, description=f'ID: {guild.id}', color=discord.Color.blurple())
        embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name='オーナー', value=guild.owner.mention)
        embed.add_field(name='メンバー数', value=guild.member_count)
        embed.add_field(name='作成日時', value=discord.utils.format_dt(guild.created_at, 'F'))
        if guild.premium_tier:
            embed.add_field(name='ブーストレベル', value=guild.premium_tier)
            embed.add_field(name='<:server_booster:1348889920353079316>ブースト数', value=guild.premium_subscription_count)
        embed.add_field(name='総チャンネル数', value=len(guild.channels))
        embed.add_field(name='<:category:1348887675729477643>カテゴリ数', value=len(guild.categories))
        embed.add_field(name='<:textchannel:1348887554912686202>テキストチャンネル数', value=len(guild.text_channels))
        embed.add_field(name='<:voicechannel:1348887595881397766>ボイスチャンネル数', value=len(guild.voice_channels))
        embed.add_field(name='<:roles:1348887353204281425>ロール数', value=len(guild.roles))
        embed.add_field(name='🧵絵文字数', value=len(guild.emojis))
        await interaction.response.send_message(embed=embed, ephemeral=True)

        

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(server(bot))