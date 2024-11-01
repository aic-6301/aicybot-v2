import discord
from discord.ext import commands
from discord import app_commands



class cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name='ping', description="BotのPingを取得します")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("Pong!:ping_pong: {0}ms".format(round(self.bot.latency * 1000)), ephemeral=True)
    
    @app_commands.command(name='help', description="ヘルプを表示します")
    async def help(self, interaction: discord.Interaction, command: str = None):
        embed = discord.Embed(title="ヘルプ")
        if command:
            embed.description = f"{command}のヘルプ"
            for cmd in self.bot.tree.walk_commands(type=discord.AppCommandType.chat_input):
                if cmd.name == command:
                    value = cmd.description
                    for param in cmd.parameters:
                        if param.choices:
                            value += f"\n選択肢: {', '.join([f'{c.name}' for c in param.choices])}"
                    embed.add_field(name="/"+cmd.name, value=value)
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
                await interaction.response.send_message("そのコマンドは存在しません", ephemeral=True)
                return
        else:
            embed.description = "コマンド一覧"
            for cmd in self.bot.tree.walk_commands(type=discord.AppCommandType.chat_input):
                if cmd.parent:
                    name = f"/{cmd.parent.name} {cmd.name}"
                else:
                    name = f"/{cmd.name}"
                if isinstance(cmd, discord.app_commands.Group):
                    continue
                embed.add_field(name=name, value=cmd.description)
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(cog(bot))