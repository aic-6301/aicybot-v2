##################################################################
# 注意: 音楽を流すBotではありません。音楽の情報を特定するコマンドです。
# 音楽を流すBotは別で作成してください。
##################################################################

import discord
from discord.ext import commands
from discord import app_commands


class spotify(commands.Cog):
    bot: commands.Bot
    
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='playing', description='現在再生している音楽の情報を表示します。')
    @app_commands.guild_only()
    @app_commands.describe(member='情報を取得するメンバー')
    async def spotify(self, interaction: discord.Interaction, member: discord.Member = None):
        if not member:
            member = interaction.guild.get_member(interaction.user.id)
        else:
            member = interaction.guild.get_member(member.id)
        if member.activities:
            for activity in member.activities:
                print(activity)
                if isinstance(activity, discord.Spotify):
                    embed = discord.Embed(title=f"{member.nick if member.nick else member.name}がSpotifyで再生中",
                                          color=discord.Colour(0x1DB954))
                    embed.add_field(name="タイトル", value=activity.title, inline=False)
                    embed.add_field(name="アーティスト", value=f"[{activity.artist}](https://google.com/search?q={activity.artist.replace(' ', '')})", inline=False)
                    embed.add_field(name="アルバム", value=f"[{activity.album}](https://google.com/search?q={activity.album})", inline=False)
                    embed.add_field(name="再生開始時間", value=f"{discord.utils.format_dt(activity.start, 'T')}", inline=False)
                    embed.set_thumbnail(url=activity.album_cover_url)
                    view = discord.ui.View()
                    view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label='Spotifyで聞く', url=activity.track_url, emoji='🔗'))
                    await interaction.response.send_message(content=f"||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​|| _ _ _ _ _ _ {activity.track_url}",embed=embed, view=view)
                    return
                elif activity.type == discord.ActivityType.listening:
                    print(activity.name)
                    if activity.name == 'YouTube Music':
                        if activity.small_image_text != "Playing":
                            await interaction.response.send_message(f"何もしていないようです。", ephemeral=True)
                            return
                        embed = discord.Embed(title = f"{activity.name}で再生中", description="これ以上の情報は不明です。", color = discord.Colour(0x1DB954))
                        embed.add_field(name = "タイトル", value = activity.details, inline = False)
                        embed.add_field(name = "詳細", value = activity.state, inline = False)
                        embed.add_field(name = "再生開始時間", value = f"{discord.utils.format_dt(activity.start, 'T')}", inline = False)
                        if activity.large_image_url:
                            embed.set_thumbnail(url = activity.large_image_url)
                        await interaction.response.send_message(embed = embed, ephemeral = True)
                        return
                    elif activity.name == 'Spotify':
                        embed = discord.Embed(title = f"{activity.name}で再生中", description="これ以上の情報は不明です。おそらくローカルファイルを再生中です。", color = discord.Colour(0x1DB954))
                        embed.add_field(name = "タイトル", value = activity.details, inline = False)
                        if activity.state:
                            embed.add_field(name = "詳細", value = activity.state, inline = False)
                        embed.add_field(name = "再生開始時間", value = f"{discord.utils.format_dt(activity.start, 'T')}", inline = False)
                        if activity.large_image_url:
                            embed.set_thumbnail(url = activity.large_image_url)
                        view = discord.ui.View()
                        view.add_item(discord.ui.Button(style = discord.ButtonStyle.link, label = '調べてみる', url = f'https://google.com/search?q={activity.details}', emoji = '🔗'))
                        await interaction.response.send_message(embed = embed, ephemeral = True, view=view)
                        return
                continue
            await interaction.response.send_message("Spotifyのコンテンツを再生していません。\n-# 注:ローカルファイルは表示されません。", ephemeral=True)
            return
        else:
            await interaction.response.send_message("何もしていないようです。", ephemeral=True)
            return

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(spotify(bot))