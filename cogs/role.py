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
        super().__init__(placeholder='ロールを選択してください...', min_values=1, max_values=1, options=options)
        self.roles = roles

    async def callback(self, interaction: discord.Interaction):
        role_id = int(self.values[0])
        role = interaction.guild.get_role(role_id)
        if role:
            try:
                if role in interaction.user.roles:
                    await interaction.user.remove_roles(role)
                    embed = discord.Embed(title='削除', description=f'{role.mention} ロールが削除されました。', color=discord.Color.blurple())
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    await interaction.user.add_roles(role)
                    embed = discord.Embed(title='追加', description=f'{role.mention} ロールが追加されました。', color=discord.Color.blurple())
                    await interaction.response.send_message(embed=embed, ephemeral=True)
            except discord.errors.Forbidden:
                embed = discord.Embed(title='エラー', description='Botの権限が不足しています。', color=discord.Color.red())
                await interaction.response.send_message(embed=embed, ephemeral=True)
            # Automatically clear the selection
            view = RoleDropdownView(self.roles)
            embed = interaction.message.embeds[0]
            await interaction.message.edit(embed=embed, view=view)
        else:
            embed = discord.Embed(title='エラー', description='ロールが見つかりませんでした。', color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)

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
    async def create_panel(self, interaction: discord.Interaction, name: str):
        database_rp.create_rolepanel(name, interaction.guild.id)
        await interaction.response.send_message(f'{name}ロールパネルが作成されました。', ephemeral=True)
    
    @group.command(name="addrole", description="ロールパネルにロールを追加します")
    async def add_role(self, interaction: discord.Interaction, name: str, role: discord.Role):
        database_rp.add_role_to_panel(name, role.id)
        if role.position >= interaction.guild.me.top_role.position:
            embed = discord.Embed(title='エラー', description='Botより上のロールを追加することはできません。', color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        await interaction.response.send_message(f'{role.mention} ロールがパネルに追加されました。', ephemeral=True)

    @group.command(name="removerole", description="ロールパネルからロールを削除します")
    async def remove_role(self, interaction: discord.Interaction, name: str, role: discord.Role):
        database_rp.remove_role_from_panel(name, role.id)
        embed = discord.Embed(title='削除', description=f'{role.mention} ロールがパネルから削除されました。', color=discord.Color.blurple())
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @group.command(name="delete", description="ロールパネルを削除します")
    async def delete_panel(self, interaction: discord.Interaction, name: str):
        database_rp.delete_rolepanel(name)
        await interaction.response.send_message(f'{name}ロールパネルが削除されました。', ephemeral=True)
    
    @group.command(name='send', description='ロールパネルを送信します')
    async def send_panel(self, interaction: discord.Interaction, name: str, channel: discord.TextChannel):
        panel = database_rp.get(name)
        if not panel:
            await interaction.response.send_message('ロールパネルが見つかりませんでした。', ephemeral=True)
            return
        roles = [interaction.guild.get_role(role_id) for role_id in database_rp.get_roles_from_panel(name)]
        if not roles:
            await interaction.response.send_message('ロールが見つかりませんでした。\nロールを設定してからもう一度送信してください。', ephemeral=True)
            return
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
        print(panels)
        options = []
        for panel in panels:
            options.append(app_commands.Choice(name=panel[1], value=panel[1]))
        return options


    async def cog_load(self):
        print('Updating role panels')
        panels = database_rp.get_all()
        for panel in panels:
            guild = self.bot.get_guild(panel[2])
            roles = [guild.get_role(role_id) for role_id in database_rp.get_roles_from_panel(panel[1])]
            if roles:
                channel = guild.get_channel(panel[4])
                if channel:
                    message = await channel.fetch_message(panel[3])
                    view = RoleDropdownView(roles)
                    embed = discord.Embed(title=panel[1], description='ロールを選択してください', color=discord.Color.blurple())
                    await message.edit(embed=embed, view=view)
                else:
                    print(f"Channel with ID {panel[4]} not found in guild {guild.name}")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(RolePanel(bot))