import discord
from discord.ext import commands
from discord import app_commands

import Paginator


disabled_NextButton = discord.ui.Button(emoji=discord.PartialEmoji(name="\U000025b6"), disabled=True)
disabled_PreviousButton = discord.ui.Button(emoji=discord.PartialEmoji(name="\U000025c0"), disabled=True)

class cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name='about', description="Botの情報を表示します")
    async def about(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Bot情報", description="-# このBotの詳しい情報は特にないようです。", color=discord.Color.dark_gold())
        embed.add_field(name="名前", value=self.bot.user.name)
        embed.add_field(name="ID", value=self.bot.user.id)
        embed.add_field(name="Botの作成日時", value=self.bot.user.created_at.strftime("%Y/%m/%d %H:%M:%S"))
        embed.add_field(name="バージョン", value="0.3")
        embed.add_field(name="開発者", value="AIC_6301")
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.set_footer(text="招待は/inviteから。")
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label='レポジトリ', url='https://github.com/aic-6301/aicybot-v2', style=discord.ButtonStyle.link, emoji='🔗'))
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @app_commands.command(name='invite', description="Botの招待リンクを表示します")
    async def invite(self, interaction: discord.Interaction, bot: discord.User = None):
        if not bot:
            bot = self.bot.user
        elif not bot.bot:
            await interaction.response.send_message("Botを指定してください", ephemeral=True)
            return
        embed = discord.Embed(title="Botの招待リンク", description="このBotを招待するためのリンクです", color=discord.Color.dark_gold())
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="管理者権限で招待",emoji="👑",style=discord.ButtonStyle.url,
                                         url=f"https://discord.com/api/oauth2/authorize?client_id={bot.id}&permissions=8&scope=bot%20applications.commands"))
        view.add_item(discord.ui.Button(label="権限を選択して招待",emoji="🔢",style=discord.ButtonStyle.url,
                                         url=f"https://discord.com/api/oauth2/authorize?client_id={bot.id}&permissions=1194000908287&scope=bot%20applications.commands"))
        view.add_item(discord.ui.Button(label="権限無しで招待",emoji="❌",style=discord.ButtonStyle.url,
                                         url=f"https://discord.com/api/oauth2/authorize?client_id={bot.id}&scope=bot%20applications.commands"))
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @app_commands.command(name='ping', description="BotのPingを取得します")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("Pong!:ping_pong: {0}ms".format(round(self.bot.latency * 1000)), ephemeral=True)
    
    @app_commands.command(name='help', description="ヘルプを表示します")
    async def help(self, interaction: discord.Interaction, command: str = None):
        embed = discord.Embed(title="ヘルプ", color=discord.Color.dark_gold())
        if command:
            for cmd in self.bot.tree.walk_commands(type=discord.AppCommandType.chat_input):
                if cmd.name == command:
                    if isinstance(cmd, discord.app_commands.Group):
                        embeds = []
                        embed.description = f"{cmd.name}コマンド\n {cmd.description}"
                        
                        for i, child in enumerate(cmd.commands):
                            value = child.description
                            for param in child.parameters:
                                if param.choices:
                                    value += f"\n選択肢: {', '.join([f'{c.name}' for c in param.choices])}"
                            embed.add_field(name=f"/{cmd.name} {child.name}", value=value)
                            
                            if (i+1) % 6 == 0:
                                embeds.append(embed)
                                embed = discord.Embed(title="ヘルプ", color=discord.Color.dark_gold())
                        
                        if len(embed.fields) > 0:
                            embeds.append(embed)
                        
                        if len(embeds) == 1:
                            await interaction.response.send_message(embed=embeds[0], ephemeral=True)
                        else:
                            await Paginator.Simple(ephemeral=True).start(interaction, embeds)
                        return
                    else:
                        embed.description = f"{command}のヘルプ"
                        value = cmd.description
                        if cmd.parent:
                            name = f"/{cmd.parent.name} {cmd.name}"
                        else:
                            name = f"/{cmd.name}"
                        for param in cmd.parameters:
                            if param.choices:
                                value += f"\n選択肢: {', '.join([f'{c.name}' for c in param.choices])}"
                        embed.add_field(name=name, value=value)
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                        return
            await interaction.response.send_message("そのコマンドは存在しません", ephemeral=True)
            return
        else:
            embeds = []
            embed.description = "コマンド一覧"
            for i, cmd in enumerate(self.bot.tree.walk_commands(type=discord.AppCommandType.chat_input)):
                if cmd.parent:
                    name = f"/{cmd.parent.name} {cmd.name}"
                else:
                    name = f"/{cmd.name}"
                if isinstance(cmd, discord.app_commands.Group):
                    continue
                embed.add_field(name=name, value=cmd.description, inline=False)
                if (i+1) % 5 == 0:
                    embeds.append(embed)
                    embed = discord.Embed(title="ヘルプ", color=discord.Color.dark_gold())
                    
            if len(embed.fields) > 0:
                embeds.append(embed)
            
            if len(embeds) == 1:
                await interaction.response.send_message(embed=embeds[0], ephemeral=True)
            else:
                await Paginator.Simple(ephemeral=True).start(interaction, embeds)
                
    

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(cog(bot))