import discord
from discord.ext import commands
from discord import app_commands

import Paginator


disabled_NextButton = discord.ui.Button(emoji=discord.PartialEmoji(name="\U000025b6"), disabled=True)
disabled_PreviousButton = discord.ui.Button(emoji=discord.PartialEmoji(name="\U000025c0"), disabled=True)

class cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
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
                            
                            if (i+1) % 5 == 0:
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