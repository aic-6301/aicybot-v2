import discord
from discord.ext import commands
from discord import app_commands

import Paginator
import string
import random

from utils import database

class change_name(discord.ui.Modal):
    def __init__(self, id):
        super().__init__(title='名前変更', timeout=None)
        
        self.value = None
        
        self.name = discord.TextInput(label='新しい名前', placeholder='新しい名前を入力してください。', required=True, style=discord.TextStyle.short)
        
        self.add_item(self.name)
        self.id = id
        
    async def on_submit(self, interaction: discord.Interaction):
        data = database.get_key('ticket', 'id', self.id)
        self.value = self.name.value
        database.update('ticket', ['name'], [self.value], 'id', self.id)
        await interaction.response.send_message(f'チケットの名前を変更しました。', ephemeral=True)
        return

class close_reason(discord.ui.Modal):
    def __init__(self):
        super().__init__(title='チケットを閉じる', timeout=None)
        
        self.value = None
        
        self.reason = discord.TextInput(label='理由', placeholder='チケットを閉じる理由を入力してください。', required=True, style=discord.TextStyle.long)
        
        self.add_item(self.reason)
    
    async def on_submit(self, interaction: discord.Interaction):
        data = database.get_key('tickets', 'channel', interaction.channel.id)
        self.value = self.reason.value
        for ticket in data:
            if ticket[4] == interaction.guild.id:
                if ticket[2] == interaction.user.id:
                    await interaction.response.send_message('自分のチケットには返信できません。', ephemeral=True)
                    return
                database.update('tickets', ['closed', 'reason'], [True, self.value], 'channel', interaction.channel.id)
                await interaction.channel.delete()
                interaction.response.pong()
                return

class SelectChannels(discord.ui.ChannelSelect):
    def __init__(self, id, guild, type):
        super().__init__(placeholder='チャンネルを選択してください。', min_values=1, max_values=1)
        self.id = id
        self.guild = guild
        self.channel_types = [discord.ChannelType.category] if type == 'category' else [discord.ChannelType.text]
                
        
    
    async def callback(self, interaction: discord.Interaction):
        data = database.get_key('ticket', 'id', self.id)
        type = 'category' if self.channel_types[0] == discord.ChannelType.category else 'channel'
        database.update('ticket', [type], [int(self.values[0].id)], 'id', self.id)
        await interaction.response.edit_message(content=f'正常に変更しました。', view=None)
        return

class SelectRole(discord.ui.RoleSelect):
    def __init__(self, id, guild):
        super().__init__(placeholder='ロールを選択してください。', min_values=1, max_values=5)
        self.id = id
        self.guild = guild

    async def callback(self, interaction: discord.Interaction):
        data = database.get_key('ticket', 'id', self.id)
        roles = [int(value.id) for value in self.values]
        database.update('ticket', ['roles'], [f'{roles}'], 'id', self.id)
        await interaction.response.edit_message(f'開かれた際にメンションされるロールを変更しました。')
        return



# チケット設定
class ticket_settings(discord.ui.View):
    def __init__(self, id):
        super().__init__(timeout=None)
        self.id = id
        
    @discord.ui.button(label='名前を変更', style=discord.ButtonStyle.primary, emoji='📝')
    async def change_name(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(view=change_name(self.id))
    
    @discord.ui.button(label='カテゴリを変更', style=discord.ButtonStyle.primary, emoji='📁')
    async def change_category(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        view = discord.ui.View()
        view.add_item(SelectChannels(self.id, guild, 'category'))
        await interaction.response.send_message('カテゴリを指定して下さい。', view=view, ephemeral=True)
    
    @discord.ui.button(label='ログチャンネルを変更', style=discord.ButtonStyle.primary, emoji='📝')
    async def change_log_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        view = discord.ui.View()
        view.add_item(SelectChannels(self.id, guild, 'text'))
        await interaction.response.send_message('ログチャンネルを指定してください。', view=view, ephemeral=True)
    
    @discord.ui.button(label='自動メンションロール', style=discord.ButtonStyle.primary, emoji='🔗')
    async def change_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        view = discord.ui.View()
        view.add_item(SelectRole(self.id, guild))
        await interaction.response.send_message('開かれた際にメンションされるロールを指定してください。', view=view, ephemeral=True)
    
    

# チケットを閉じる頭悪いエディション
class close_ticket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
    
    @discord.ui.button(label='閉じる', style=discord.ButtonStyle.danger, emoji='🗑️')
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        print('fire')
        ch = interaction.channel
        data = database.get_key('tickets', 'channel', interaction.channel.id)
        for ticket in data:
            if ticket[3] == ch.id:
                print(ticket)
                d = database.get_key('ticket', 'id', ticket[1])
                print(d)
                log_ch = interaction.guild.get_channel(d[0][4])
                em = discord.Embed(title='チケット', description=f'{interaction.user.mention} がチケットを閉じました。', color=discord.Color.red())
                em.add_field(name='チケット', value=f'<#{ch.id}>')
                em.add_field(name='チケットID', value=f'{ticket[5]}')
                em.add_field(name='作成者', value=f'<@{ticket[2]}>')
                em.add_field(name='閉じた人', value=f'{interaction.user.mention}')
                await log_ch.send(embed=em)
                messages = [message async for message in ch.history(limit=None)]
                database.update('tickets', ['closed', 'messages'], [True, f'{messages}'], 'channel', ch.id)
                await interaction.channel.delete()
                interaction.response.pong()
                return
        await interaction.response.send_message('チケットが見つかりません。', ephemeral=True)

class ticket(commands.Cog):
    bot: commands.Bot

    def __init__(self, bot):
        self.bot = bot
    
    tickets = app_commands.Group(name='ticket', description='チケットに関するコマンドです')

    @tickets.command(name='create', description='チケットを作成します。')
    @app_commands.describe(name='チケットの名前',category='チケットを作成するカテゴリを設定します。', log_ch='チケットのログを保存するチャンネルを設定します。')
    @app_commands.default_permissions(manage_guild=True)
    async def create(self, interaction: discord.Interaction, name: str, category: discord.CategoryChannel, log_ch: discord.TextChannel):
        data = database.get_key('ticket', 'guild', interaction.guild.id)
        if data:
            for ticket in data:
                print(ticket)
                if ticket[2] == name:
                    await interaction.response.send_message(f'同じ名前のチケットが既に存在します。', ephemeral=True)
                    return
            if len(data) >= 3 and not data[6]:
                await interaction.response.send_message(f'作成可能なチケットの上限に達しています。', ephemeral=True)
                return
        id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        database.insert_or_update('ticket', ['id', 'guild', 'name', 'category', 'channel'], [id, interaction.guild.id, name, category.id, log_ch.id], 'guild', interaction.guild.id)
        await interaction.response.send_message(f'チケットを作成しました。', ephemeral=True)
    
    @tickets.command(name='delete', description='チケットを削除します。')
    @app_commands.describe(name='チケットの名前')
    @app_commands.default_permissions(manage_guild=True)
    async def delete(self, interaction: discord.Interaction, name: str):
        data = database.get_key('ticket', 'guild', interaction.guild.id)
        for ticket in data:
            if ticket[2] == name:
                database.delete('ticket', 'id', ticket[0])
                await interaction.response.send_message(f'チケットを削除しました。', ephemeral=True)
                return
        await interaction.response.send_message(f'チケットが見つかりません。', ephemeral=True)
    
    @tickets.command(name='list', description='チケットの一覧を表示します。')
    @app_commands.default_permissions(manage_guild=True)
    async def list(self, interaction: discord.Interaction):
        data = database.get('ticket', interaction.guild.id)
        embed = discord.Embed(title='チケット一覧')
        embeds = []
        for i, ticket in enumerate(data):
            embed.add_field(name=ticket[2], value=f'カテゴリ: <#{ticket[3]}> ログチャンネル: <#{ticket[4]}>')
            
            if (i+1) % 10 == 0:
                embeds.append(embed)
                embed = discord.Embed(title='チケット一覧')
        
        if len(embed.fields) > 0:
            embeds.append(embed)
        
        if len(embeds) == 1:
            await interaction.response.send_message(embed=embeds[0], ephemeral=True)
        else:
            await Paginator.Simple(ephemeral=True).start(interaction, embeds)
    
    
    @tickets.command(name='send', description='チケットを送信します。')
    @app_commands.describe(name='チケットの名前', channel='送信するチャンネル')
    @app_commands.default_permissions(manage_guild=True)
    async def send(self, interaction: discord.Interaction, name: str, channel: discord.TextChannel):
        data = database.get_key('ticket', 'guild', interaction.guild.id)
        for ticket in data:
            print(ticket)
            if ticket[2] == name:
                view = discord.ui.View()
                view.add_item(discord.ui.Button(label='チケットを開く', style=discord.ButtonStyle.primary, emoji='🎫', custom_id='create_ticket'))
                embed = discord.Embed(title=ticket[2], description='チケットはこちらから')
                await channel.send(embed=embed, view = view)
                await interaction.response.send_message(f'チケットを送信しました。', ephemeral=True)
                return
        await interaction.response.send_message(f'チケットが見つかりません。', ephemeral=True)
    
    @tickets.command(name='setting', description='チケットの設定を変更します。')
    @app_commands.describe(name='チケットの名前')
    async def setting(self, interaction: discord.Interaction, name: str):
        data = database.get_key('ticket', 'guild', interaction.guild.id)
        for ticket in data:
            if ticket[2] == name:
                await interaction.response.send_message('設定を変更します。', view=ticket_settings(ticket[0]), ephemeral=True)
                return
        await interaction.response.send_message(f'チケットが見つかりません。', ephemeral=True)
    
    
    # チケット作成とか
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.data.get('custom_id') and interaction.data['custom_id'] == 'create_ticket':
            data = database.get_key('ticket', 'guild', interaction.guild.id)
            for ticket in data:
                if ticket[2] == interaction.message.embeds[0].title:                    
                    data = database.get_key('tickets', 'guild', interaction.guild.id)

                    for t in data:
                        if t[2] == interaction.user.id and not t[7]:
                            await interaction.response.send_message(f'既にチケットを作成しています。\nチケットはこちら:<#{t[3]}>', ephemeral=True)
                            return

                    number = 0
                    for i in range(1, 1000):
                        d = database.get_key('tickets', 'number', i)
                        print(d)
                        if not d:
                            number = i
                            break
                    category = interaction.guild.get_channel(ticket[3])
                    log_ch = interaction.guild.get_channel(ticket[4])
                    admin_role = interaction.guild.get_role(ticket[6])
                    overwrites = {
                        interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                        interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    }
                    if admin_role:
                        overwrites[admin_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
                    channel = await category.create_text_channel(name=f'チケット-{number}', overwrites=overwrites)
                    view = discord.ui.View()
                    view.add_item(discord.ui.Button(label='チケットを閉じる', style=discord.ButtonStyle.danger, emoji='🗑️', custom_id='close_ticket'))
                    view.add_item(discord.ui.Button(label='チケットを閉じる', style=discord.ButtonStyle.danger, emoji='🗑️', custom_id='close_ticket_reason'))
                    view.add_item(discord.ui.Button(label='チケットを担当する', style=discord.ButtonStyle.green, emoji='🖐️', custom_id='response_ticket'))
                    embed = discord.Embed(title='チケット', description='チケットを作成しました。', color=discord.Color.blurple())
                    mention = ''
                    roles = ticket[5].replace('[', '').replace(']', '').replace(' ', '').split(',')
                    for role in roles:
                        print(role)
                        mention += f'<@&{role}> '
                    id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                    database.insert('tickets', ['id', 'ticket_id', 'guild', 'user', 'channel', 'number'], [id, ticket[0], interaction.guild.id, interaction.user.id, channel.id, number, ])
                    msg = await channel.send(content=f'{interaction.user.mention} {mention}',embed=embed, view=view)
                    await msg.edit(content='',embed=embed, view=view)
                    em = discord.Embed(title='チケット', description=f'{interaction.user.mention} がチケットを作成しました。', color=discord.Color.blurple())
                    em.add_field(name='チケット', value=f'<#{channel.id}>')
                    em.add_field(name='チケットID', value=f'{number}')
                    em.add_field(name='作成者', value=f'{interaction.user.mention}')
                    await log_ch.send(embed=em)
                    await interaction.response.send_message(f'チケットを作成しました。\nチケットはこちら:<#{channel.id}>', ephemeral=True)
                    return
            await interaction.response.send_message(f'チケットが見つかりません。', ephemeral=True)

        if interaction.data.get('custom_id') and interaction.data['custom_id'] == 'close_ticket':
            await interaction.response.send_message('チケットを閉じますか？', view=close_ticket())
        
        if interaction.data.get('custom_id') and interaction.data['custom_id'] == 'close_ticket_reason':
            await interaction.response.send_modal(view=close_reason())
        
        if interaction.data.get('custom_id') and interaction.data['custom_id'] == 'response_ticket':
            number = interaction.channel.name.split('-')[1]
            data = database.get_key('tickets', 'number', number)
            for ticket in data:
                if ticket[4] == interaction.guild.id:
                    if ticket[2] == interaction.user.id:
                        await interaction.response.send_message('自分のチケットには返信できません。', ephemeral=True)
                        return
                    database.update('tickets', ['responser'], [interaction.user.id], 'number', number)
                    embed = discord.Embed(title='チケットの担当', description=f'このチケットは{interaction.user.mention}が対応します。', color=discord.Color.blurple())
                    await interaction.response.send_message(embed=embed)
                    view = discord.ui.View()
                    view.add_item(discord.ui.Button(label='チケットを閉じる', style=discord.ButtonStyle.danger, emoji='🗑️', custom_id='close_ticket'))
                    view.add_item(discord.ui.Button(label='理由をつけてチケットを閉じる', style=discord.ButtonStyle.danger, emoji='🗑️', custom_id='close_ticket_reason'))
                    await interaction.message.edit(view=view)
                    return
    
    # 自動コンプリート
    @send.autocomplete("name")
    @delete.autocomplete("name")
    @setting.autocomplete("name")
    async def _name_autocomplete(self, interaction: discord.Interaction, name: str):
        panels = database.get_key('ticket', 'guild', interaction.guild.id, 'name')
        options = []
        for panel in panels:
            options.append(app_commands.Choice(name=panel[0], value=panel[0]))
        return options
                
        
        

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ticket(bot))