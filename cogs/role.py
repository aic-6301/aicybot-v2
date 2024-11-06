import discord
from discord.ext import commands
from discord import app_commands
from utils import database_rp

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
        database_rp.create_rolepanel(name, interaction.guild.id)
        await interaction.response.send_message(f'{name}ロールパネルが作成されました。', ephemeral=True)
    
    @group.command(name="addrole", description="ロールパネルにロールを追加します")
    @app_commands.describe(name='ロールパネルの名前', role='追加するロール')
    async def add_role(self, interaction: discord.Interaction, name: str, role: discord.Role):
        database_rp.add_role_to_panel(name, role.id)
        if role.position >= interaction.guild.me.top_role.position:
            embed = discord.Embed(title='エラー', description='Botより上のロールを追加することはできません。', color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        await interaction.response.send_message(f'{role.mention} ロールがパネルに追加されました。', ephemeral=True)

    @group.command(name="removerole", description="ロールパネルからロールを削除します")
    @app_commands.describe(name='ロールパネルの名前', role='削除するロール')
    async def remove_role(self, interaction: discord.Interaction, name: str, role: discord.Role):
        database_rp.remove_role_from_panel(name, role.id)
        embed = discord.Embed(title='削除', description=f'{role.mention} ロールがパネルから削除されました。', color=discord.Color.blurple())
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @group.command(name="delete", description="ロールパネルを削除します")
    @app_commands.describe(name='ロールパネルの名前')
    async def delete_panel(self, interaction: discord.Interaction, name: str):
        database_rp.delete_rolepanel(name)
        await interaction.response.send_message(f'{name}ロールパネルが削除されました。', ephemeral=True)
    
    @group.command(name='send', description='ロールパネルを送信します')
    @app_commands.describe(name='ロールパネルの名前', channel='送信するチャンネル')
    async def send_panel(self, interaction: discord.Interaction, name: str, channel: discord.TextChannel):
        panel = database_rp.get(name)
        if not panel:
            await interaction.response.send_message('ロールパネルが見つかりませんでした。\nパネルを作成してからもう一度お試しください。', ephemeral=True)
            return
        roles = [interaction.guild.get_role(role_id) for role_id in database_rp.get_roles_from_panel(name)]
        if not roles:
            await interaction.response.send_message('ロールが見つかりませんでした。\nロールを設定してからもう一度お試しください。', ephemeral=True)
            return
        if panel[3]:
            old_ch = interaction.guild.get_channel(panel[4])
            old_msg = await old_ch.fetch_message(panel[3])
            await old_msg.delete()
        view = RoleDropdownView(roles)
        embed = discord.Embed(title=panel[1], description='ロールを選択してください', color=discord.Color.blurple())
        message = await channel.send(embed=embed, view=view)
        database_rp.set_panel_message(name, message.id, message.channel.id)
        await interaction.response.send_message(f'{name}ロールパネルが送信されました。', ephemeral=True)
    
    
    
    @send_panel.autocomplete("name")
    @add_role.autocomplete("name")
    @remove_role.autocomplete("name")
    async def _name_autocomplete(self, interaction: discord.Interaction, name: str):
        panels = database_rp.get_guild_panels(interaction.guild.id)
        options = []
        for panel in panels:
            options.append(app_commands.Choice(name=panel[1], value=panel[1]))
        return options


    async def cog_load(self):
        self.bot.logger.debug('Updating role panels')
        panels = database_rp.get_all()
        for panel in panels:
            guild = self.bot.get_guild(panel[2])
            if not guild:
                self.bot.logger.error(f"Guild with ID {panel[2]} not found")
                database_rp.delete_rolepanel(panel[1])
                continue
            roles = [guild.get_role(role_id) for role_id in database_rp.get_roles_from_panel(panel[1])]
            if roles:
                channel = guild.get_channel(panel[4])
                if channel:
                    message = await channel.fetch_message(panel[3])
                    view = RoleDropdownView(roles)
                    embed = discord.Embed(title=panel[1], description='ロールを選択してください', color=discord.Color.blurple())
                    await message.edit(embed=embed, view=view)
                else:
                    self.bot.logger.error(f"Channel with ID {panel[4]} not found in guild {guild.name}")
                    view = RoleDropdownView(roles)
                    embed = discord.Embed(title=panel[1], description='ロールを選択してください', color=discord.Color.blurple())
                    await channel.send(embed=embed, view=view)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(RolePanel(bot))