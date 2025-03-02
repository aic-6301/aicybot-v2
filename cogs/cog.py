import discord
from discord.ext import commands, tasks
from discord import app_commands

import Paginator
import asyncio
import datetime

disabled_NextButton = discord.ui.Button(emoji=discord.PartialEmoji(name="\U000025b6"), disabled=True)
disabled_PreviousButton = discord.ui.Button(emoji=discord.PartialEmoji(name="\U000025c0"), disabled=True)

class cog(commands.Cog):
    bot: commands.Bot
    
    def __init__(self, bot):
        self.bot = bot
        self.rpc = 0
        self.change_status.start()
    
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
            
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.errors.BadArgument):
            await ctx.reply(embed=discord.Embed(title="エラー - Bad Argument", 
                                                description="指定された引数がエラーを起こしているため実行出来ません。", 
                                                color=discord.Color.red(), timestamp=ctx.message.created_at))
        elif isinstance(error, commands.errors.CommandNotFound):
            await ctx.reply(embed=discord.Embed(title="エラー - Command Not Found", 
                                                description="コマンドが存在しません。", 
                                                color=discord.Color.red(), 
                                                timestamp=ctx.message.created_at))
        elif isinstance(error, commands.errors.CommandOnCooldown):
            await ctx.reply(embed=discord.Embed(title="クールダウン", 
                                                description="コマンドはクールダウン中です。"+
                                                f"\n{discord.utils.format_dt(error.retry_after, style='R')}後に再度実行してください。", 
                                                color=discord.Color.red(), 
                                                timestamp=ctx.message.created_at))
        elif isinstance(error, commands.errors.MemberNotFound):
            await ctx.reply(embed=discord.Embed(title="エラー - Member Not Found", 
                                                description="メンバーが存在しません。", 
                                                color=discord.Color.red(), 
                                                timestamp=ctx.message.created_at))
        elif isinstance(error, commands.errors.UserNotFound):
            await ctx.reply(embed=discord.Embed(title="エラー - User Not Found", 
                                                description="ユーザーが存在しません", 
                                                color=discord.Color.red(), 
                                                timestamp=ctx.message.created_at))
        elif isinstance(error, commands.errors.MissingPermissions):
            await ctx.reply(embed=discord.Embed(title="エラー - Missing Permissions", 
                                                description="権限が不足しています。", 
                                                color=discord.Color.red(), 
                                                timestamp=ctx.message.created_at))
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.reply(embed=discord.Embed(title="エラー - Missing Required Argument", 
                                                description="必要な引数が足りません。", 
                                                color=discord.Color.red(), 
                                                timestamp=ctx.message.created_at))
        elif isinstance(error, commands.errors.BotMissingPermissions):
            await ctx.reply(embed=discord.Embed(title="エラー - Bot Missing Permissions", 
                                                description="Botが実行するのに必要な権限が足りません。", 
                                                color=discord.Color.red(), 
                                                timestamp=ctx.message.created_at))
        else:
            await ctx.reply(embed=discord.Embed(title="エラー - Unknown Error", 
                                                description=f"エラーが発生しました。\nエラー内容：{error} \nエラーID:{ctx.message.id}", 
                                                color=discord.Color.red(), 
                                                timestamp=ctx.message.created_at
                                                ).set_footer(
                                                    text="エラーIDをコピーして、お問い合わせサーバーまでお問い合わせください。"
                                                ))
        embed = discord.Embed(title="エラー情報", description="", color=discord.Color.red(), timestamp=ctx.message.created_at)
        embed.add_field(name="エラー内容", value=error, inline=False)
        embed.add_field(name="エラーID", value=ctx.message.id, inline=False)
        embed.add_field(name="実行ユーザー", value=f"{ctx.author.name} ({ctx.author.id})", inline=False)
        embed.add_field(name="実行サーバー", value=f"{ctx.guild.name} ({ctx.guild.id})", inline=False)
        await self.bot.get_channel(1033496616130334784).send(embed=embed)
    
    @commands.Cog.listener()
    async def on_app_command_error(self, interaction:discord.Interaction, error: discord.app_commands.AppCommandError):
        if isinstance(error, discord.app_commands.errors.BotMissingPermissions):
            await interaction.response.send_message(
                embed=discord.Embed(title="エラー - Bot Missing Permissions", 
                                    description="Botが実行するのに必要な権限が足りません。", 
                                    color=discord.Color.red(), 
                                    timestamp=interaction.message.created_at
                                    ))
        elif isinstance(error, discord.app_commands.errors.CommandOnCooldown):
            await interaction.response.send_message(
                embed=discord.Embed(title="クールダウン",
                                    description=f"コマンドはクールダウン中です。\n{discord.utils.format_dt(error.retry_after, style='R')}後に再度実行してください。",
                                    color=discord.Color.red(),
                                    timestamp=interaction.message.created_at
                                    ))
        else:
            await interaction.response.send_message(
                embed=discord.Embed(title="エラー - Unknown Error",
                                    description=f"エラーが発生しました。\nエラー内容：{error} \nエラーID:{interaction.message.id}",
                                    color=discord.Color.red(),
                                    timestamp=interaction.message.created_at
                                    ).set_footer(text="エラーIDをコピーして、お問い合わせサーバーまでお問い合わせください。")
                )
        embed = discord.Embed(title="Error Info", description="", color=discord.Color.red(), timestamp=interaction.message.created_at)
        embed.add_field(name="エラー内容", value=error, inline=False)
        embed.add_field(name="エラーID", value=interaction.message.id, inline=False)
        embed.add_field(name="実行ユーザー", value=f"{interaction.user.name} ({interaction.user.id})", inline=False)
        embed.add_field(name="実行サーバー", value=f"{interaction.guild.name} ({interaction.guild.id})", inline=False)
        await self.bot.get_channel(1033496616130334784).send(embed=embed)
        
    @tasks.loop(seconds=10)
    async def change_status(self):
        if self.rpc == 0:
            await self.bot.change_presence(activity=discord.CustomActivity(name=f'{len(self.bot.guilds)} Guilds | {len(self.bot.users)} Users'))
            self.rpc = 1
        elif self.rpc == 1:
            await self.bot.change_presence(activity=discord.CustomActivity(name=f'/help | More at /about'))
            self.rpc = 2
        elif self.rpc == 2:
            time = datetime.datetime.now() - self.bot.uptime
            await self.bot.change_presence(activity=discord.CustomActivity(name=f'起動時間: {time.days + '日' if time.days > 0 else ''} {time.seconds // 3600}時間{time.seconds // 60 % 60}分{time.seconds % 60 + '秒'  if time.days > 0 else ''}'))
            self.rpc = 0

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(cog(bot))