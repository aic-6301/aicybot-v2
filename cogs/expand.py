import discord
from discord.ext import commands
from discord import app_commands
import re

from utils import database

regex_discord_message_url = (
    '(?!<)https://(ptb.|canary.)?discord(app)?.com/channels/'
    '(?P<guild>[0-9]{17,20})/(?P<channel>[0-9]{17,20})/(?P<message>[0-9]{17,20})(?!>)'
)
class expand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if database.get('expand', message.guild.id)[1]:
            await _expand(message)
    
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.data.get('custom_id') and interaction.data['custom_id'] == 'delete-expand':
            await deexpand(interaction)
        

async def _expand(message: discord.Message):
    messages = await get_message(message)
    for m in messages:
        embeds = []
        embed = discord.Embed(color=discord.Color.brand_green())
        embeds.append(embed)
        
        embeds[0].set_author(name=m.author.display_name, icon_url=m.author.avatar.url)
        
        if m.content or m.attachments:
            if m.attachments:
                for at in m.attachments[:1]:
                    embeds[0].set_image(url=at.url)
            if m.content:
                embeds[0].description = m.content
        
        if m.embeds:
            for em in m.embeds[:2]:
                embeds.append(em)
        view = discord.ui.View()
        view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label='メッセージに飛ぶ', url=m.jump_url, emoji='🔗'))
        view.add_item(discord.ui.Button(style=discord.ButtonStyle.danger, label='削除', custom_id='delete-expand', emoji='🗑️'))

        await message.reply(embeds=embeds, mention_author=False, view=view)


async def deexpand(interaction: discord.Interaction):
    await interaction.message.delete()
    await interaction.response.send_message("削除しました。", ephemeral=True)
        
            
        
    
    
async def get_message(message):
    messages = []
    for ids in re.finditer(regex_discord_message_url, message.content):
        if message.guild.id != int(ids['guild']):
            continue
        channel = message.guild.get_channel(int(ids['channel']))
        message = await channel.fetch_message(int(ids['message']))
        messages.append(message)
    return messages
        

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(expand(bot))