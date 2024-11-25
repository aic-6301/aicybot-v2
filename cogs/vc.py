import discord
from discord.ext import commands
from discord import app_commands

from utils import database


def is_owner(member):
    return member.id == database.get_key('voice_channels', 'owner', member.id, 'owner')


class user_select(discord.ui.Select):
    def __init__(self, channel, mode):
        self.mode = mode
        options = []
        for member in channel.members:
            if not member.bot:
                options.append(discord.SelectOption(label=member.display_name, value=str(member.id)))
        super().__init__(placeholder='ユーザーを選択してください', options=options)
    
    async def callback(self, interaction: discord.Interaction):
        member = interaction.guild.get_member(int(self.values[0]))
        if self.mode == 'owner':
            await interaction.channel.edit(topic=f'オーナー: {member.mention}')
            database.update('voice_channels', ['owner'], [member.id], 'channel', interaction.channel.id)
            await interaction.response.send_message('オーナーを設定しました。', ephemeral=True)
        if self.mode == 'kick':
            if member == interaction.user:
                await interaction.response.send_message('自分自身をキックすることはできません。', ephemeral=True)
                return
            await member.move_to(None)
            await interaction.response.send_message(f'{member.mention}を切断しました。', ephemeral=True)


class panel(discord.ui.View):
    def __init__(self, bot):
        super().__init__()
        self.timeout = None
        self.bot = bot.bot
        
    @discord.ui.button(label='通常モード', style=discord.ButtonStyle.primary, emoji='✅', row=1)
    async def normal(self, button: discord.ui.Button, interaction: discord.Interaction):
        if is_owner(interaction.user):
            await interaction.channel.edit(user_limit=0, nsfw=False)
            await interaction.response.send_message('通常モードに変更しました。', ephemeral=True)
        else:
            await interaction.response.send_message('あなたはこのチャンネルのオーナーではありません。', ephemeral=True)
        
    @discord.ui.button(label='ロックモード', style=discord.ButtonStyle.secondary, emoji='🔒', row=1)
    async def lock(self, button: discord.ui.Button, interaction: discord.Interaction):
        if is_owner(interaction.user):
            await interaction.channel.edit(user_limit=1)
            await interaction.response.send_message('ロックモードに変更しました。', ephemeral=True)
        else:
            await interaction.response.send_message('あなたはこのチャンネルのオーナーではありません。', ephemeral=True)
        
    @discord.ui.button(label='NSFWモード', style=discord.ButtonStyle.red, emoji='🔞', row=1)
    async def nsfw(self, button: discord.ui.Button, interaction: discord.Interaction):
        if is_owner(interaction.user):
            await interaction.channel.edit(nsfw=True)
            await interaction.response.send_message('NSFWモードに変更しました。', ephemeral=True)
        else:
            await interaction.response.send_message('あなたはこのチャンネルのオーナーではありません。', ephemeral=True)
    
    @discord.ui.button(label='オーナー変更', style=discord.ButtonStyle.secondary, emoji='👑', row=1)
    async def owner(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message('オーナーを選択してください。', ephemeral=True, view=user_select(interaction.channel, 'owner'))
        
    @discord.ui.button(label='キックする', style=discord.ButtonStyle.secondary, emoji='🦵', row=1)
    async def owner(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message('オーナーを選択してください。', ephemeral=True, view=user_select(interaction.channel, 'kick'))


class vc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    group = app_commands.Group(name="vc", description="ボイスチャンネル関連のコマンド")
    
    
    @group.command(name="panel", description="ボイスチャンネルパネルを表示します")
    async def vc_panel(self, interaction: discord.Interaction):
        pass
    
    async def send_panel(self, channel):
        embed = discord.Embed(title='パネル', description='いろんな設定ができます', color=discord.Color.blurple())

    
    async def set_owner(self, member, channel):
        database.update('vc_panel', ['owner'], [member.id], 'channel', channel.id)
        await channel.edit(topic=f'オーナー: {member.mention}')
        return
    
    async def purge(self, channel):
        database.update('vc_panel', ['owner'], [0], 'channel', channel.id)
        await channel.edit(user_limit=0, nsfw=False, topic=None)
        await channel.send(embed=discord.Embed(title='チャンネルリセット中・・・', description='誰もいなくなったためチャンネルをリセットしています・・・', color=discord.Color.blurple()))
        await channel.purge(limit=None)
        return
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.bot:
            if before.channel != after.channel:
                 if database.get('vc_panel', after.channel.guild.id):
                    if not database.get_key('voice_channels', 'channel', after.channel.id):
                        database.insert_or_update('voice_channels',
                                                  ['guild', 'channel', 'owner', 'default_name'], 
                                                  [after.channel.guild.id, after.channel.id, 0, after.channel.name],
                                                  'channel',
                                                  after.channel.id)
                    if not database.get_key('voice_channels', 'channel', after.channel.id, 'owner'):
                        await self.set_owner(member, after.channel)
                    else:
                        pass
                    embed = discord.Embed(title='入退室通知', description=f'{member.mention} が {after.channel.name} に参加しました', color=discord.Color.green())
                    await after.channel.send(embed=embed)
            elif before.channel and after.channel is None:
                if database.get('vc_panel', before.channel.guild.id):
                    embed = discord.Embed(title='入退室通知', description=f'{member.mention} が {before.channel.name} から退出しました', color=discord.Color.red())
                    await before.channel.send(embed=embed)
                    
                    m = []
                    
                    for members in before.channel.members:
                        if members.bot:
                            pass
                        m.append(members)
                    
                    if len(m) == 0:
                        for members in before.channel.members:
                            await members.move_to(None)
                            await self.purge(before.channel)
                            return
                    
                    if member.id == database.get_key('voice_channels', before.channel.guild.id, 'owner'):
                        await self.set_owner(m[0], before.channel)            
                
                    

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(vc(bot))