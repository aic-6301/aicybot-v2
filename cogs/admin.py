import discord
from discord.ext import commands
from discord import app_commands

import subprocess
import sys


class reboot(discord.ui.View):
    def __init__(self):
        super().__init__()
    
    @discord.ui.button(label="サービスを再起動する。", style=discord.ButtonStyle.red, emoji="🔴")
    async def reboot(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("再起動します。", ephemeral=True)
        sys.exit()


class admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    group = app_commands.Group(name="admin", description="Bot管理者用コマンド", default_permissions=discord.Permissions(administrator=True))
    
    @group.command(name="reload", description="コグを再読み込みします")
    async def reload(self, interaction: discord.Interaction, file: str):
        if not commands.is_owner():
            await interaction.response.send_message('このコマンドはBot管理者のみ実行できます。', ephemeral=True)
            return
        try:
            await self.bot.reload_extension(f"cogs.{file}")
            await interaction.response.send_message(f"{file}を再読み込みしました。", ephemeral=True)
        except commands.ExtensionNotLoaded:
            await interaction.response.send_message(f"{file}は読み込まれていません。", ephemeral=True)
        except commands.ExtensionNotFound:
            await interaction.response.send_message(f"{file}は存在しません。", ephemeral=True)
        except commands.ExtensionFailed as e:
            await interaction.response.send_message(f"{file}の読み込みに失敗しました。\nエラー内容:{e}", ephemeral=True)
    
    @group.command(name='update', description="Botをアップデートします")
    async def update(self, interaction: discord.Interaction):
        
        if not await self.bot.is_owner(interaction.user):
            await interaction.response.send_message('このコマンドはBot管理者のみ実行できます。', ephemeral=True)
            return
        
        embed = discord.Embed(title="⏲️アップデート", description="アップデートを開始します", color=discord.Color.dark_gold())
        await interaction.response.send_message(embed=embed, ephemeral=False)
        process = subprocess.run(['git', 'pull', 'origin', 'main'], capture_output=True, text=True)
        
        if process.returncode == 0:
            if "Already up to date." in process.stdout:
                embed.title = "✅アップデート"
                embed.description = "アップデートは不要です。"
                await interaction.edit_original_response(embed=embed)
                return
            else:
                embed.title = "✅アップデート"
                embed.description = f'アップデート完了。\n ```{process.stdout}```'
                await interaction.edit_original_response(embed=embed, view=reboot())
        else:
            embed.title = "❌エラー"
            embed.description = f'エラーが発生しました。\n ```{process.stderr}```'
            embed.color = discord.Color.red()
            await interaction.edit_original_response(embed=embed)
            return

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(admin(bot))