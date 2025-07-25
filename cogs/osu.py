import discord
from discord.ext import commands
from discord import app_commands

from utils import osu as osuapi
from utils import database
import re

from Paginator import Simple

import matplotlib.pyplot as plt
import io
from datetime import datetime
import requests

class getBeatmapView(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="譜面の詳細を取得", style=discord.ButtonStyle.green)
    async def get_beatmap(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        beatmap_id = interaction.message.embeds[0].footer.text
        if not beatmap_id.isdigit():
            await interaction.response.send_message("Beatmap IDが取得できませんでした。", ephemeral=True)
            return

        data = osuapi.get_beatmap(beatmap_id)
        if not data:
            await interaction.response.send_message("指定したBeatmapが見つかりませんでした。", ephemeral=True)
            return
        
        embed = discord.Embed(title=f"{data['title']} - {data['artist']}", color=discord.Color.dark_gold(), url=data['url'])
        embed.set_thumbnail(url=data['covers']['list'])
        embed.add_field(name="難易度", value=data['version'], inline=False)
        embed.add_field(name="BPM", value=data['bpm'], inline=False)
        embed.add_field(name="プレイ数", value=data['playcount'], inline=False)
        embed.add_field(name="ダウンロード数", value=data['download_count'], inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class osu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    
    async def draw_graph(self, user):
        data = requests.get(f"https://spring-queen-e9b5.suzuki435423.workers.dev/?user={user}").json()
        
        fig = plt.figure(figsize=(10, 3))
        ax = fig.subplots()
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        
        x = []
        y = []
        
        for i in range(len(data)):
            datetimeobj = datetime.strptime(data[i]['timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ')
            y.append(datetimeobj.strftime('%Y-%m-%d'))
            x.append(data[i]['score'])

        ax.plot(y, x, color='yellow', linestyle='-', linewidth=2, markersize=5)

        fig.set_facecolor('#2a2326')
        ax.set_facecolor('#2a2326')
        ax.xaxis.label.set_color('#ffffff')
        ax.yaxis.label.set_color('#ffffff')
        plt.gca().axis('off')
        
        plt.gca().invert_xaxis()
        plt.gca().invert_yaxis()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        
        plt.close(fig)
        return buf

    group = app_commands.Group(name="osu", description="osu!関連のコマンド")
    
    @group.command(name="link", description="osu!アカウントをリンクします (ユーザー入力無しで自分の情報をすぐに取得できます。)")
    @app_commands.describe(user='osu!ユーザー名')
    async def link(self, interaction: discord.Interaction, user: str):
        await interaction.response.defer(thinking=True)
        if not user:
            await interaction.followup.send("ユーザー名を指定してください。", ephemeral=True)
            return
        
        if user.isdigit():
            user = int(user)
        else:
            user = '@' + user
        apiuser = osuapi.get_user(user)
        if not apiuser:
            await interaction.followup.send("指定したユーザーが見つかりませんでした。", ephemeral=True)
            return
        
        database.insert_or_update('osu_users', ['user_id', 'osu_user'], [interaction.user.id, apiuser["id"]])
        await interaction.followup.send(f"{user}をあなたのosu!アカウントとしてリンクしました。", ephemeral=True)

    @group.command(name="unlink", description="osu!アカウントのリンクを解除します")
    async def unlink(self, interaction: discord.Interaction):
        if not database.get_key('osu_users', 'user_id', interaction.user.id):
            await interaction.response.send_message("osu!アカウントがリンクされていません。", ephemeral=True)
            return
        
        database.delete('osu_users', 'user_id', interaction.user.id)
        await interaction.response.send_message("osu!アカウントのリンクを解除しました。", ephemeral=True)
    
    @group.command(name="user", description="ユーザーの情報を取得します")
    @app_commands.describe(user='ユーザー名')
    async def user(self, interaction: discord.Interaction, user: str = None):
        await interaction.response.defer(thinking=True)
        duser = database.get_key('osu_users', 'user_id', interaction.user.id)
        print(duser)
        if not user and not duser:
            await interaction.followup.send("osu!アカウントがリンクされていません。/osu linkでリンクしてください。", ephemeral=True)
            return
        user = user or duser[0][1]
        if user.isdigit():
            user = int(user)
        else:
            user = '@'+user
        # try:

        data = osuapi.get_user(user)
        if not data:
            await interaction.followup.send("指定したユーザーが見つかりませんでした。", ephemeral=True)
            return
        supporter = " 💸" if data['is_supporter'] else ""
        
        graph = await self.draw_graph(user)
        
        embed = discord.Embed(title=f"{data['username']}の情報 {supporter}", color=discord.Color.dark_gold(), url=f'https://osu.ppy.sh/users/{data["id"]}')
        embed.set_thumbnail(url=data['avatar_url'])
        embed.set_image(url=data['cover_url'])
        embed.add_field(name="✨ PP", value=f"{data['statistics']['pp']:.0f}", inline=False)
        embed.add_field(name="🏆 国内ランキング / 世界ランキング", value=f"#{str(data['statistics']['country_rank'])} / #{(data['statistics']['global_rank'])}", inline=False)
        embed.add_field(name="🎚️ レベル", value=data['statistics']['level']['current'], inline=False)
        embed.add_field(name="🎯 精度", value=f"{data['statistics']['hit_accuracy']:.2f}%", inline=False)
        embed.add_field(name="⌛ プレイ時間 / プレイ回数", value=f"{data['statistics']['play_time'] // 3600}時間 / {data['statistics']['play_count']}回", inline=False)
        if graph:
            embed.set_image(url='attachment://graph.png')
            await interaction.followup.send(embed=embed, file=discord.File(graph, filename='graph.png'))
        else:
            await interaction.followup.send(embed=embed)
        # except Exception as e:
        #     await interaction.followup.send(f"エラーが発生しました。\n```{e}```", ephemeral=True)
        
    
    @group.command(name="recent", description="最近のプレイを取得します (過去24時間のプレイ)")
    @app_commands.describe(user='ユーザー名')
    async def recent(self, interaction: discord.Interaction, user: str = None):
        await interaction.response.defer(thinking=True)
        duser = database.get_key('osu_users', 'user_id', interaction.user.id)
        print(duser)
        if not user and not duser:
            await interaction.followup.send("osu!アカウントがリンクされていません。/osu linkでリンクしてください。", ephemeral=True)
            return
        user = user or duser[0][1]
        if user.isdigit():
            user = int(user)
        else:
            user = '@'+user
        # try:
        user_api = osuapi.get_user(user)
        data = osuapi.get_recent(user_api['id'])
        print(data)
        if not data:
            await interaction.followup.send("最近のプレイが見つかりませんでした。", ephemeral=True)
            return
        embeds = []
        
        for play in data:
            
            beatmap = osuapi.get_beatmap(play['beatmap']['id'])
            if not beatmap:
                continue
            
            if play['max_combo'] == beatmap['max_combo']:
                combo =  f"✨"
            elif play['perfect']:
                combo = "🌟"
            else:
                combo = ""
            
            if play['pp'] is None:
                pp = 0
            else:
                pp = f"{float(play['pp']):.2f}"


            embed = discord.Embed(title=f"{play['beatmapset']['title']}@{play['beatmap']['version']} ({play['beatmap']['status']})", 
                                  color=discord.Color.dark_gold(), 
                                  url=play['beatmap']['url'])
            embed.set_image(url=play['beatmapset']['covers']['cover'])
            embed.add_field(name="🥁 コンボ", 
                            value=f"{combo}{play['max_combo']}/{beatmap['max_combo'] if play['passed'] else '😱失敗'}", 
                            inline=False)
            embed.add_field(name="300 / :100:100 / 50 / :x:miss", 
                            value=f"{play['statistics']['count_300']} / {play['statistics']['count_100']} / {play['statistics']['count_50']} / {play['statistics']['count_miss']}", 
                            inline=False)
            embed.add_field(name="🎵 スコア", value=play['score'], inline=False)
            embed.add_field(name="✨ PP", value=f"{pp}", inline=True)
            embed.add_field(name="🎯 精度", value=f"{float(play['accuracy'] * 100):.2f}%", inline=True)
            embed.add_field(name="🏅 ランク", value=play['rank'], inline=True)
            embed.add_field(name="⌛ プレイ時間", value=play['created_at'], inline=False)
            embed.add_field(name="📘 難易度", value=play['beatmap']['difficulty_rating'], inline=True)
            embed.add_field(name="🎛️ BPM", value=beatmap['bpm'], inline=True)
            embed.add_field(name="🛠️ Mod", value=', '.join(play['mods']) if play['mods'] else 'なし', inline=False)
            embed.set_footer(text=play['beatmap']['beatmapset_id'])
            embeds.append(embed)

        if len(embeds) == 1:
            await interaction.followup.send(embed=embeds[0], view=getBeatmapView())
            return
        else:
            await Simple(timeout=None).start(interaction, embeds)
            return

        # except Exception as e:
        #     await interaction.response.send_message(f"エラーが発生しました。\n```{e}```", ephemeral=True)
        #     return
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        
        if 'https://osu.ppy.sh/' in message.content:
            try:
                data = database.get_key('osu_expand', 'guild', message.guild.id)
                if not data or not data[0][1]:
                    return
                match = re.search(r'osu\.ppy\.sh/beatmapsets/(\d+)/', message.content)
                if match:
                    beatmapset_id = match.group(1)
                    data = osuapi.get_beatmap(beatmapset_id)
                    if data:
                        embed = discord.Embed(title=f"{data['title']} - {data['artist']}", color=discord.Color.dark_gold(), url=data['url'])
                        embed.set_thumbnail(url=data['covers']['list'])
                        embed.add_field(name="難易度", value=data['version'], inline=False)
                        embed.add_field(name="🎛️ BPM", value=data['bpm'], inline=False)
                        embed.add_field(name="プレイ数", value=data['playcount'], inline=False)
                        embed.add_field(name="⬇️ ダウンロード数", value=data['download_count'], inline=False)
                        embed.set_author(name=data['creator'], icon_url=data['creator_avatar_url'])
                        embed.set_footer(text=data['id'])
                        await message.reply(embed=embed, mention_author=False)
                    return
                match = re.search(r'osu\.ppy\.sh/users/(\d+)', message.content)
                if match:
                    user_id = match.group(1)
                    data = osuapi.get_user(user_id)
                    if data:
                        supporter = " 💸" if data['is_supporter'] else ""
                        
                        graph = await self.draw_graph(user_id)
                        
                        embed = discord.Embed(title=f"{data['username']}の情報 {supporter}", color=discord.Color.dark_gold(), url=f'https://osu.ppy.sh/users/{data['id']}')
                        embed.set_thumbnail(url=data['avatar_url'])
                        embed.set_image(url=data['cover_url'])
                        embed.add_field(name="✨ PP", value=f"{data['statistics']['pp']:.0f}", inline=False)
                        embed.add_field(name="🏆 国内ランキング / 世界ランキング", value=f"#{str(data['statistics']['country_rank'])} / #{(data['statistics']['global_rank'])}", inline=False)
                        embed.add_field(name="🎚️ レベル", value=data['statistics']['level']['current'], inline=False)
                        embed.add_field(name="🎯 精度", value=f"{data['statistics']['hit_accuracy']:.2f}%", inline=False)
                        
                        if graph:
                            embed.set_image(url='attachment://graph.png')
                            await message.reply(embed=embed, file=discord.File(graph, filename='graph.png'), mention_author=False)
                        else:
                            await message.reply(embed=embed, mention_author=False)
                    return
            except Exception as e:
                pass

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(osu(bot))