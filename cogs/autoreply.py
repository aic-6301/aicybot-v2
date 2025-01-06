import discord
from discord.ext import commands
from discord import app_commands

import random
import string
import re

import Paginator

from utils import database


class autoreply(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    group = app_commands.Group(name="autoreply", description="自動返信の設定を行います")
    
    @group.command(name="add", description="自動返信を追加します")
    @app_commands.describe(keyword='キーワード(re:をつけてregex対応。\nfull:で完全一致。)', reply='返信内容(reply:で返信させる。\nreact:でリアクションをつける。\nrandom:でランダムに返信)')
    async def add(self, interaction: discord.Interaction, keyword: str, reply: str):
        if sum(prefix in keyword for prefix in ['re:', 'full:']) > 1 or sum(prefix in reply for prefix in ['reply:', 'react:', 'random:']) > 1:
            await interaction.response.send_message('キーワードまたは返信内容にコマンドが二つ以上指定されています。', ephemeral=True)
            return
        _id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        try:
            database.insert_or_update('autoreply', ['id', 'keyword', 'reply', 'user', 'guild'], [str(_id), str(keyword), str(reply), int(interaction.user.id), int(interaction.guild.id)])
            embed = discord.Embed(title='自動返信を追加', description=f'キーワード: `{keyword}`\n返信内容: `{reply}`\n `/autoreply delete content:{_id}` または、`/autoreply delete content:{keyword}`で削除できます。', color=discord.Color.blurple())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        except Exception as e:
            print(e)
            await interaction.response.send_message('エラーが発生しました。もう一度試してください。', ephemeral=True)
            return
    
    @group.command(name="delete", description="自動返信を削除します")
    @app_commands.describe(content='削除するキーワードまたはID(キーワードの場合は同じキーワードをすべて削除されます。)')
    async def delete(self, interaction: discord.Interaction, content: str):
        if database.get_key('autoreply', 'keyword', content):
            data = database.get_key('autoreply', 'keyword', content)
            database.delete('autoreply', 'keyword', content)
            replies = [data_item[2] for data_item in data]
            embed = discord.Embed(title='自動返信を削除', description=f'キーワード: `{content}`\n> 削除された返信内容\n `{"`\n`".join(replies)}`', color=discord.Color.blurple())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        elif database.get_key('autoreply', 'id', content):
            data = database.get_key('autoreply', 'id', content)
            database.delete('autoreply', 'id', content)
            replies = [data_item[2] for data_item in data]
            embed = discord.Embed(title='自動返信を削除', description=f'ID: `{content}`\n> 削除された返信内容\n {"`\n`".join(replies)}', color=discord.Color.blurple())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        else:
            await interaction.response.send_message('そのキーワード・IDは存在しません。', ephemeral=True)
            return
    
    @group.command(name="list", description="自動返信のリストを表示します")
    async def list(self, interaction: discord.Interaction):
        autoreplies = database.get_key('autoreply', 'guild', interaction.guild.id)
        if not autoreplies:
            await interaction.response.send_message('自動返信は何も設定されていません。', ephemeral=True)
            return
        embeds = []
        embed = discord.Embed(title='自動返信リスト', color=discord.Color.blurple())
        for i, autoreply in enumerate(autoreplies):
            field_value = f'キーワード:{autoreply[1]}\n返信内容:{autoreply[2][:300] + "..." if len(autoreply[2]) > 300 else autoreply[2]}\n登録者: <@{autoreply[3]}>'
            embed.add_field(name=f'ID: `{autoreply[0]}`', value=field_value)
            if (i+1) % 10 == 0:
                embeds.append(embed)
                embed = discord.Embed(title='自動返信リスト', color=discord.Color.blurple())
        if len(embed.fields) > 0:
            embeds.append(embed)
        if len(embeds) == 1:
            await interaction.response.send_message(embed=embeds[0], ephemeral=True)
        else:
            await Paginator.Simple(ephemeral=True).start(interaction, embeds)
        return
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.guild is None:
            return
        autoreplies = database.get_key('autoreply', 'guild', message.guild.id)
        if not autoreplies:
            return
        for autoreply in autoreplies:
            if autoreply[1].startswith('re:'):
                if re.search(rf'{(autoreply[1][3:])}', message.content):
                    if autoreply[2].startswith('noreply:'):
                        await message.channel.send(autoreply[2][6:])
                    elif autoreply[2].startswith('react:'):
                        await message.add_reaction(autoreply[2][6:])
                    elif autoreply[2].startswith('random:'):
                        random_replies = [ar[2][7:] for ar in autoreplies if ar[1] == autoreply[1] and ar[2].startswith('random:')]
                        if random_replies:
                            await message.reply(random.choice(random_replies), mention_author=False)
                    else:
                        await message.reply(autoreply[2], mention_author=False)
            elif autoreply[1].startswith('full:'):
                if autoreply[1][5:] == message.content:
                    if autoreply[2].startswith('noreply:'):
                        await message.channel.send(autoreply[2][6:])
                    elif autoreply[2].startswith('react:'):
                        await message.add_reaction(autoreply[2][6:])
                    elif autoreply[2].startswith('random:'):
                        random_replies = [ar[2][7:] for ar in autoreplies if ar[1] == autoreply[1] and ar[2].startswith('random:')]
                        if random_replies:
                            await message.reply(random.choice(random_replies), mention_author=False)
                    else:
                        await message.reply(autoreply[2], mention_author=False)
            else:
                if autoreply[1] in message.content:
                    if autoreply[2].startswith('noreply:'):
                        await message.channel.send(autoreply[2][6:])
                    elif autoreply[2].startswith('react:'):
                        await message.add_reaction(autoreply[2][6:])
                    elif autoreply[2].startswith('random:'):
                        random_replies = [ar[2][7:] for ar in autoreplies if ar[1] == autoreply[1] and ar[2].startswith('random:')]
                        if random_replies:
                            await message.reply(random.choice(random_replies), mention_author=False)
                    else:
                        await message.reply(autoreply[2], mention_author=False)
        return

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(autoreply(bot))