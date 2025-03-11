import discord
from discord.ext import commands
from discord import app_commands

from utils import database

class autopublish(commands.Cog):
    bot: commands.Bot

    def __init__(self, bot):
        self.bot = bot


        
    autopublish = app_commands.Group(name='publish', description='自動公開に関するコマンドです')
    
    @autopublish.command(name='add', description='自動公開するチャンネルを追加します。')
    @app_commands.describe(channel='自動公開するチャンネルを指定します。')
    @app_commands.default_permissions(manage_guild=True)
    async def add(self, interaction: discord.Interaction, channel: discord.TextChannel):
        data = database.get_key('autopublish', 'guild', interaction.guild.id)
        if data and len(data[0]) >= 5 and not data[0][2]:
            await interaction.response.send_message('自動公開設定可能なチャンネル数は最大5個までです。', ephemeral=True)
            return
        
        if database.get_key('autopublish', 'channel', channel.id):
            await interaction.response.send_message('指定したチャンネルは既に設定されています。', ephemeral=True)
            return
        
        if channel.type != discord.ChannelType.news:
            await interaction.response.send_message('このチャンネルはアナウンスチャンネルではありません。', ephemeral=True)
            return
        
        if data:
            data = eval(data[0][1])  # Convert text back to dict
            data.append(channel.id)
            channels = str(data)  # Convert dict back to text
            database.update('autopublish', ['channel'], [channels], key_value=interaction.guild.id)
        else:
            channels = str([channel.id])
        
            database.insert('autopublish', ['channel', 'guild'], [channels, interaction.guild.id])
        await interaction.response.send_message(f'{channel.mention}を自動公開対象に追加しました。', ephemeral=True)
        return

    @autopublish.command(name='remove', description='自動公開するチャンネルを削除します。')
    @app_commands.describe(channel='自動公開するチャンネルを指定します。')
    @app_commands.default_permissions(manage_guild=True)
    async def remove(self, interaction: discord.Interaction, channel: discord.TextChannel):
        data = database.get_key('autopublish', 'guild', interaction.guild.id)
        if not data:
            await interaction.response.send_message('設定されているチャンネルがありません。', ephemeral=True)
            return
        
        data = eval(data[0][1])  # Convert text back to dict
        if channel.id not in data:
            await interaction.response.send_message('指定したチャンネルは設定されていません。', ephemeral=True)
            return
        
        data.remove(channel.id)
        if data:
            channels = str(data)  # Convert dict back to text
        else:
            channels = '0'
        
        database.update('autopublish', ['channel'], [channels], key_value=interaction.guild.id)
        await interaction.response.send_message(f'{channel.mention}を自動公開対象から削除しました。', ephemeral=True)
        return

    @autopublish.command(name='list', description='自動公開するチャンネルを表示します。')
    @app_commands.default_permissions(manage_guild=True)
    async def list(self, interaction: discord.Interaction):
        data = database.get_key('autopublish', 'guild', interaction.guild.id)
        if not data:
            await interaction.response.send_message('設定されているチャンネルがありません。', ephemeral=True)
            return
        
        data = eval(data[0][1])  # Convert text back to dict
        for channel in data:
            if not interaction.guild.get_channel(channel):
                data.remove(channel)
        channels = [interaction.guild.get_channel(channel).mention for channel in data]
        if not channels:
            await interaction.response.send_message('設定されているチャンネルがありません。', ephemeral=True)
            return
        await interaction.response.send_message(f'自動公開対象のチャンネルは以下の通りです。\n{", ".join(channels)}', ephemeral=True)
        return

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        
        data = database.get_key('autopublish', 'guild', message.guild.id)
        if not data:
            return
        
        print(data)
        data = eval(data[0][1])  # Convert text back to dict
        if message.channel.id in data:
            await message.publish()
        return

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(autopublish(bot))