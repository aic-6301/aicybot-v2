import discord
from discord.ext import commands
from discord import app_commands
from utils import database

class RoleDropdown(discord.ui.Select):
    def __init__(self, roles):
        options = [
            discord.SelectOption(label=role.name, value=str(role.id))
            for role in roles
        ]
        maxv = len(options)
        super().__init__(placeholder='ロールを選択してください...', min_values=1, max_values=maxv, options=options)
        self.roles = roles

    async def callback(self, interaction: discord.Interaction):
        role_ids = [int(value) for value in self.values]
        roles = [interaction.guild.get_role(role_id) for role_id in role_ids]
        added_roles = []
        removed_roles = []
        try:
            for role in roles:
                if role:
                    if role in interaction.user.roles:
                        await interaction.user.remove_roles(role)
                        removed_roles.append(role)
                    else:
                        await interaction.user.add_roles(role)
                        added_roles.append(role)
                else:
                    embed = discord.Embed(title='エラー', description='ロールが見つかりませんでした。', color=discord.Color.red())
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    view = RoleDropdownView(self.roles)
                    embed = interaction.message.embeds[0]
                    await interaction.message.edit(embed=embed, view=view)
                    return

            if added_roles or removed_roles:
                description = '以下のロールを更新しました。\n'
                if added_roles:
                    description += '追加されたロール: ' + ', '.join([role.mention for role in added_roles]) + '\n'
                if removed_roles:
                    description += '削除されたロール: ' + ', '.join([role.mention for role in removed_roles])
                embed = discord.Embed(title='ロール更新', description=description, color=discord.Color.blurple())
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except discord.errors.Forbidden:
            embed = discord.Embed(title='エラー', description=f'{role.mention}ロールの付与に失敗しました。\n内容：`Botの権限が不足しています。`', color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)

        # Automatically clear the selection
        view = RoleDropdownView(self.roles)
        embed = interaction.message.embeds[0]
        await interaction.message.edit(embed=embed, view=view)
        return

class RoleDropdownView(discord.ui.View):
    def __init__(self, roles):
        super().__init__()
        self.timeout = None
        self.add_item(RoleDropdown(roles))

class RolePanel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    group = app_commands.Group(name='rolepanel', description='ロールパネルに関するコマンドです')


    @group.command(name="create", description="ロールパネルを作成します")
    @app_commands.describe(name='ロールパネルの名前')
    async def create_panel(self, interaction: discord.Interaction, name: str):
        if database.get_key('role_panels', 'guild', interaction.guild.id, 'name') == name:
            await interaction.response.send_message('その名前のロールパネルは既に存在します。', ephemeral=True)
            return
        database.insert_or_update('role_panels', ['name', 'guild'], [name, interaction.guild.id])
        await interaction.response.send_message(f'{name}ロールパネルが作成されました。', ephemeral=True)
    
    @group.command(name="addrole", description="ロールパネルにロールを追加します")
    @app_commands.describe(name='ロールパネルの名前', role='追加するロール')
    async def add_role(self, interaction: discord.Interaction, name: str, role: discord.Role):
        panel = database.get_key('role_panels', 'name', name, 'id')
        print(panel)
        if panel:
            if role.position >= interaction.guild.me.top_role.position:
                embed = discord.Embed(title='エラー', description='Botより上のロールを追加することはできません。', color=discord.Color.red())
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            database.insert_or_update('panel_roles', ['panel_id', 'role_id'], [panel[0][0], role.id])
            await interaction.response.send_message(f'{role.mention} ロールがパネルに追加されました。', ephemeral=True)

    @group.command(name="removerole", description="ロールパネルからロールを削除します")
    @app_commands.describe(name='ロールパネルの名前', role='削除するロール')
    async def remove_role(self, interaction: discord.Interaction, name: str, role: discord.Role):
        database.delete('panel_roles', 'role_id', role.id)
        embed = discord.Embed(title='削除', description=f'{role.mention} ロールがパネルから削除されました。', color=discord.Color.blurple())
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @group.command(name="delete", description="ロールパネルを削除します")
    @app_commands.describe(name='ロールパネルの名前')
    async def delete_panel(self, interaction: discord.Interaction, name: str):
        database.delete('role_panels', 'name', name)
        await interaction.response.send_message(f'{name}ロールパネルが削除されました。', ephemeral=True)
    
    @group.command(name='send', description='ロールパネルを送信します')
    @app_commands.describe(name='ロールパネルの名前', channel='送信するチャンネル')
    async def send_panel(self, interaction: discord.Interaction, name: str, channel: discord.TextChannel):
        panel = database.get_key('role_panels', 'name', name)
        for p in panel:
            if p[1] == name:
                panel = p
                break
        if not panel:
            await interaction.response.send_message('ロールパネルが見つかりませんでした。\nパネルを作成してからもう一度お試しください。', ephemeral=True)
            return
        role_ids = database.get_key('panel_roles', 'panel_id', panel[0], 'role_id')
        if role_ids == []:
            await interaction.response.send_message('ロールが見つかりませんでした。\nロールを設定してからもう一度お試しください。', ephemeral=True)
            return
        roles = [interaction.guild.get_role(role_id[0]) for role_id in role_ids]
        if roles is None:
            await interaction.response.send_message('ロールが見つかりませんでした。\nロールを設定してからもう一度お試しください。', ephemeral=True)
            return
        if panel[3]:
            old_ch = interaction.guild.get_channel(panel[4])
            old_msg = await old_ch.fetch_message(panel[3])
            await old_msg.delete()
        view = RoleDropdownView(roles)
        embed = discord.Embed(title=panel[1], description='ロールを選択してください', color=discord.Color.blurple())
        message = await channel.send(embed=embed, view=view)
        database.insert_or_update('role_panels', ['message_id', 'channel_id'], [message.id, message.channel.id], key_column='name', key_value=name)
        await interaction.response.send_message(f'{name}ロールパネルが送信されました。', ephemeral=True)
    
    
    
    @send_panel.autocomplete("name")
    @add_role.autocomplete("name")
    @remove_role.autocomplete("name")
    async def _name_autocomplete(self, interaction: discord.Interaction, name: str):
        panels = database.get_key('role_panels', 'guild', interaction.guild.id, 'name')
        options = []
        for panel in panels:
            options.append(app_commands.Choice(name=panel[0], value=panel[0]))
        return options


    async def cog_load(self):
        self.bot.logger.debug('Updating role panels')
        panels = database.get_all('role_panels')
        for panel in panels:
            guild = self.bot.get_guild(panel[2])
            if not guild:
                self.bot.logger.error(f"Guild with ID {panel[2]} not found")
                database.delete('role_panels', 'name', panel[1])
                continue
            try:
                role_ids = database.get_key('panel_roles', 'panel_id', panel[0], 'role_id')
                if role_ids == []:
                    self.bot.logger.error(f"Error fetching roles for panel {panel[1]}")
                    continue
                roles = [guild.get_role(role_id[0]) for role_id in role_ids]
            except Exception as e:
                self.bot.logger.error(f"Error fetching roles for panel {panel[1]} \n{e}")
                continue
            if roles:
                channel = guild.get_channel(panel[4])
                if channel:
                    message = await channel.fetch_message(panel[3])
                    view = RoleDropdownView(roles)
                    embed = discord.Embed(title=panel[1], description='ロールを選択してください', color=discord.Color.blurple())
                    await message.edit(embed=embed, view=view)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(RolePanel(bot))