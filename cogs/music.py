##################################################################
# 注意: 音楽を流すBotではありません。音楽の情報を特定するコマンドです。
# 音楽を流すBotは別で作成してください。
##################################################################

import discord
from discord.ext import commands
from discord import app_commands

from utils.locale import t

class spotify(commands.Cog):
    bot: commands.Bot
    
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name = 'playing', description = app_commands.locale_str("music.description"))
    @app_commands.guild_only()
    @app_commands.describe(member = app_commands.locale_str("music.member_description"))
    async def spotify(self, interaction: discord.Interaction, member: discord.Member = None):
        if not member:
            m = interaction.guild.get_member(interaction.user.id)
        else:
            m = interaction.guild.get_member(member.id)
        if m.activities:
            for activity in m.activities:
                if isinstance(activity, discord.Spotify):
                    embed = discord.Embed(title = t(m.guild.preferred_locale.value, "music.spotify_playing", user=m.display_name),
                                          color = discord.Colour(0x1DB954))
                    embed.add_field(name = t(m.guild.preferred_locale.value, "music.title"),     value = f"[{activity.title}]({activity.track_url}", inline = False)
                    embed.add_field(name = t(m.guild.preferred_locale.value, "music.artist"), value = f"[{activity.artist}](https://google.com/search?q={activity.artist.replace(' ', '+')})", inline = False)
                    embed.add_field(name = t(m.guild.preferred_locale.value, "music.album"),     value = f"[{activity.album}](https://google.com/search?q={activity.album.replace(' ', '+')})", inline = False)
                    embed.add_field(name = t(m.guild.preferred_locale.value, "music.start_time"), value = f"{discord.utils.format_dt(activity.start, 'T')}", inline = False)
                    embed.set_thumbnail(url = activity.album_cover_url)
                    view = discord.ui.View()
                    view.add_item(discord.ui.Button(style = discord.ButtonStyle.link, label = t(m.guild.preferred_locale.value, "music.listen_on_spotify"), url = activity.track_url, emoji = '🔗'))
                    await interaction.response.send_message(embed = embed, view = view, ephemeral = True if member else False)
                    return
                elif activity.type == discord.ActivityType.listening:
                    if activity.name == 'YouTube Music':
                        if activity.small_image_text != "Playing":
                            await interaction.response.send_message(t(interaction.locale.value, 'music.nothing'), ephemeral = True)
                            return
                        embed = discord.Embed(title = t(interaction.locale.value, "music.user_playing", user=m.display_name, activity=activity.name), description = t(interaction.locale.value, "music.over"), color = discord.Colour(0x1DB954))
                        embed.add_field(name = t(m.guild.preferred_locale.value, "music.title"),    value = activity.details, inline = False)
                        embed.add_field(name = t(m.guild.preferred_locale.value, "music.details"),        value = activity.state, inline = False)
                        embed.add_field(name = t(m.guild.preferred_locale.value, "music.start_time"), value = f"{discord.utils.format_dt(activity.start, 'T')}", inline = False)
                        if activity.large_image_url:
                            embed.set_thumbnail(url = activity.large_image_url)
                        await interaction.response.send_message(embed = embed, ephemeral = True if member else False)
                        return
                    elif activity.name == 'Spotify':
                        embed = discord.Embed(title = t(interaction.locale.value, "music.user_playing", user=m.display_name, activity=activity.name), description = t(interaction.locale.value, "music.over"), color = discord.Colour(0x1DB954))
                        embed.add_field(name = t(m.guild.preferred_locale.value, "music.title"), value = activity.details, inline = False)
                        if activity.state:
                            embed.add_field(name = t(m.guild.preferred_locale.value, "music.detail"), value = activity.state, inline = False)
                        embed.add_field(name = t(m.guild.preferred_locale.value, "music.started_at"), value = f"{discord.utils.format_dt(activity.start, 'T')}", inline = False)
                        embed.add_field(name = t(m.guild.preferred_locale.value, "music.length"), value = f"{activity.end - activity.start}", inline = False)
                        if activity.large_image_url:
                            embed.set_thumbnail(url = activity.large_image_url)
                        view = discord.ui.View()
                        view.add_item(discord.ui.Button(style = discord.ButtonStyle.link, label = t(m.guild.preferred_locale.value, "music.search"), url = f'https://google.com/search?q={activity.details.replace(' ', '+')}', emoji = '🔗'))
                        await interaction.response.send_message(embed = embed, view = view, ephemeral = True if member else False)
                        return
                continue
            await interaction.response.send_message(t(interaction.locale.value, "music.not_playing"), ephemeral = True)
            return
        else:
            await interaction.response.send_message(t(interaction.locale.value, "music.nothing"), ephemeral = True)
            return

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(spotify(bot))