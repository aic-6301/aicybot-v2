import discord
from discord.ext import commands
from discord import app_commands

from utils import osu as osuapi
from utils import database
import re

from Paginator import Simple

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
        
    group = app_commands.Group(name="osu", description="osu!関連のコマンド")
    
    @group.command(name="link", description="osu!アカウントをリンクします (ユーザー入力無しで自分の情報をすぐに取得できます。)")
    @app_commands.describe(user='osu!ユーザー名')
    async def link(self, interaction: discord.Interaction, user: str):
        if not user:
            await interaction.response.send_message("ユーザー名を指定してください。", ephemeral=True)
            return
        
        if user.isdigit():
            user = int(user)
        else:
            user = '@' + user
        apiuser = osuapi.get_user(user)
        if not apiuser:
            await interaction.response.send_message("指定したユーザーが見つかりませんでした。", ephemeral=True)
            return
        
        database.insert_or_update('osu_users', ['user_id', 'osu_user'], [interaction.user.id, apiuser["id"]])
        await interaction.response.send_message(f"{user}をあなたのosu!アカウントとしてリンクしました。", ephemeral=True)
    
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
        duser = database.get_key('osu_users', 'user_id', interaction.user.id)
        print(duser)
        if not user and not duser:
            await interaction.response.send_message("osu!アカウントがリンクされていません。/osu linkでリンクしてください。", ephemeral=True)
            return
        user = user or duser[0][1]
        if user.isdigit():
            user = int(user)
        else:
            user = '@'+user
        try:
            data = osuapi.get_user(user)
            embed = discord.Embed(title=f"{data['username']}の情報", color=discord.Color.dark_gold(), url=f'https://osu.ppy.sh/users/{data["id"]}')
            embed.set_thumbnail(url=data['avatar_url'])
            embed.set_image(url=data['cover_url'])
            embed.add_field(name="✨ PP", value=f"{data['statistics']['pp']:.0f}", inline=False)
            embed.add_field(name="🏆 国内ランキング / 世界ランキング", value=f"#{str(data['statistics']['country_rank'])} / #{(data['statistics']['global_rank'])}", inline=False)
            embed.add_field(name="🎚️ レベル", value=data['statistics']['level']['current'], inline=False)
            embed.add_field(name="🎯 精度", value=f"{data['statistics']['hit_accuracy']:.2f}%", inline=False)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            print(data)
            await interaction.response.send_message(f"エラーが発生しました。\n```{e}```", ephemeral=True)
        
    
    @group.command(name="recent", description="最近のプレイを取得します (過去24時間のプレイ)")
    @app_commands.describe(user='ユーザー名')
    async def recent(self, interaction: discord.Interaction, user: str = None):
        duser = database.get_key('osu_users', 'user_id', interaction.user.id)
        print(duser)
        if not user and not duser:
            await interaction.response.send_message("osu!アカウントがリンクされていません。/osu linkでリンクしてください。", ephemeral=True)
            return
        user = user or duser[0][1]
        if user.isdigit():
            user = int(user)
        else:
            user = '@'+user
        # try:
        data = osuapi.get_recent(user)
        print(data)
        if not data:
            await interaction.response.send_message("最近のプレイが見つかりませんでした。", ephemeral=True)
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
            
            
            embed = discord.Embed(title=f"{play['beatmapset']['title']}", color=discord.Color.dark_gold(), url=play['beatmap']['url'])
            embed.set_thumbnail(url=play['beatmapset']['covers']['list'])
            embed.add_field(name="🥁 コンボ", 
                            value=f"{combo}{play['max_combo']}/{beatmap['max_combo'] if play['passed'] else '😱失敗'}", inline=False)
            embed.add_field(name="🎵 スコア", value=play['score'], inline=False)
            embed.add_field(name="✨ PP", value=f"{float(play['pp']):.2f}", inline=False)
            embed.add_field(name="🎯 精度", value=f"{float(play['accuracy'] * 100):.2f}%", inline=False)
            embed.add_field(name="⌛ プレイ時間", value=play['created_at'], inline=False)
            embed.add_field(name="🅰️ ランク", value=play['rank'], inline=False)
            embed.add_field(name="🛠️ Mod", value=', '.join(play['mods']) if play['mods'] else 'なし', inline=False)
            embed.set_footer(text=play['beatmap']['beatmapset_id'])
            embeds.append(embed)

        if len(embeds) == 1:
            await interaction.response.send_message(embed=embeds[0], view=getBeatmapView())
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
                    embed.add_field(name="難易度", value=data['difficulty_rating'], inline=False)
                    embed.add_field(name="BPM", value=data['bpm'], inline=False)
                    embed.add_field(name="プレイ数", value=data['playcount'], inline=False)
                    embed.add_field(name="ダウンロード数", value=data['download_count'], inline=False)
                    await message.reply(embed=embed, mention_author=False, view=getBeatmapView())
                return
            match = re.search(r'osu\.ppy\.sh/users/(\d+)', message.content)
            if match:
                user_id = match.group(1)
                data = osuapi.get_user(user_id)
                if data:
                    embed = discord.Embed(title=f"{data['username']}の情報", color=discord.Color.dark_gold(), url=f'https://osu.ppy.sh/users/{data['id']}')
                    embed.set_thumbnail(url=data['avatar_url'])
                    embed.add_field(name="✨ PP", value=f"{data['statistics']['pp']:.0f}", inline=False)
                    embed.add_field(name="🏆 国内ランキング / 世界ランキング", value=f"#{str(data['statistics']['country_rank'])} / #{(data['statistics']['global_rank'])}", inline=False)
                    embed.add_field(name="🎚️ レベル", value=data['statistics']['level']['current'], inline=False)
                    embed.add_field(name="🎯 精度", value=f"{data['statistics']['hit_accuracy']:.2f}%", inline=False)
                    await message.reply(embed=embed, mention_author=False)
            return

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(osu(bot))