import discord
from discord.ext import commands
from discord import app_commands


class spotify(commands.Cog):
    bot: commands.Bot
    
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='spotify', description='あなたが現在再生しているSpotifyの情報を表示します。')
    @app_commands.guild_only()
    @app_commands.describe(member='Spotify情報を取得するメンバー')
    async def spotify(self, interaction: discord.Interaction, member: discord.Member = None):
        if not member:
            member = interaction.guild.get_member(interaction.user.id)
        else:
            member = interaction.guild.get_member(member.id)
        if member.activities:
            for activity in member.activities:
                if isinstance(activity, discord.Spotify):
                    embed = discord.Embed(title=f"{member.nick if member.nick else member.name}がSpotifyで再生中",
                                          color=discord.Colour(0x1DB954))
                    embed.add_field(name="タイトル", value=activity.title, inline=False)
                    embed.add_field(name="アーティスト", value=activity.artist, inline=False)
                    embed.add_field(name="アルバム", value=activity.album, inline=False)
                    embed.add_field(name="再生開始時間", value=f"{discord.utils.format_dt(activity.start, 'T')}", inline=False)
                    embed.set_thumbnail(url=activity.album_cover_url)
                    view = discord.ui.View()
                    view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label='Spotifyで聞く', url=activity.track_url, emoji='🔗'))
                    await interaction.response.send_message(embed=embed, view=view)
                    return
                continue
            await interaction.response.send_message("Spotifyを再生していません。", ephemeral=True)
        else:
            await interaction.response.send_message("何もしていないようです。", ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(spotify(bot))