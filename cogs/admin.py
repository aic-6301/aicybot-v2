import discord
from discord.ext import commands
from discord import app_commands

import subprocess
import sys

from utils import database


class reboot(discord.ui.View):
    def __init__(self):
        super().__init__()
    
    @discord.ui.button(label="サービスを再起動する。", style=discord.ButtonStyle.red, emoji="🔴")
    async def reboot(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("再起動しています...", ephemeral=True)
        sys.exit()


class admin(commands.Cog):
    bot: commands.Bot
    
    def __init__(self, bot):
        self.bot = bot
    
    group = app_commands.Group(name="admin", description="Bot管理者用コマンド", default_permissions=discord.Permissions(administrator=True))
    
    @group.command(name="reload", description="コグを再読み込みします")
    async def reload(self, interaction: discord.Interaction, file: str):
        if not await self.bot.is_owner(interaction.user):
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
                await interaction.edit_original_response(embed=embed, view=reboot())
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
    
    @group.command(name='unti', description="チケットの数∞にする")
    async def unlimit_tickets(self, interaction: discord.Interaction, guild: int):
        if not await self.bot.is_owner(interaction.user):
            await interaction.response.send_message('このコマンドはBot管理者のみ実行できます。', ephemeral=True)
            return
        guild = self.bot.get_guiod(guild)
        if guild is None:
            await interaction.response.send_message('サーバーが見つかりませんでした。', ephemeral=True)
        database.update('ticket', ['unlimited'], [1], key_value=guild.id)
        await interaction.response.send_message('チケットの数を∞にしました。', ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(admin(bot))