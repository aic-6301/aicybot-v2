import discord
from discord.ext import commands, tasks
from discord import app_commands

from utils import database

class logger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channels = {}
        self.cache_channel_loop.start()
    
    def cache_channel(self):
        for guild in self.bot.guilds:
            data = database.get('log', guild.id)
            self.channels[guild.id] = guild.get_channel(data[2]) if data else None
        self.bot.logger.debug('Log Channels Cached.')
        
    @tasks.loop(minutes=3)
    async def cache_channel_loop(self):
        self.cache_channel()
        
    async def cog_unload(self):
        self.cache_channel_loop.stop()
    
    # メッセージ編集
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot or before.guild is None:
            return
        if before.content == after.content:
            return
        embed = discord.Embed(title="📝 - メッセージ編集", 
                              description=f"{before.author.mention}がメッセージを編集しました。", 
                              color=discord.Color.orange())
        embed.add_field(name="編集前", value=before.content)
        embed.add_field(name="編集後", value=after.content)
        embed.add_field(name="メッセージリンク", value = after.jump_url, inline=False)
        embed.add_field(name="チャンネル", value=before.channel.mention, inline=False)
        if self.channels[before.guild.id] is not None:
            await self.channels[before.guild.id].send(embed=embed)
    
    # メッセージ削除
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Role):
        if message.author.bot or message.guild is None:
            return
        embed = discord.Embed(title="🗑️ - メッセージ削除", 
                              description=f"{message.author.mention}がメッセージを削除しました。", 
                              color=discord.Color.red())
        embed.add_field(name="内容", value=message.content)
        embed.add_field(name="チャンネル", value=message.channel.mention)
        if self.channels[message.guild.id] is not None:
            await self.channels[message.guild.id].send(embed=embed)
        
    
    # ロール作成
    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        embed = discord.Embed(title="➕ - ロール作成", 
                              description=f"{role.mention}が作成されました。", 
                              color=discord.Color.green())
        embed.add_field(name="名前", value=role.name)
        embed.add_field(name="ID", value=role.id)
        embed.add_field(name="色", value=role.color)
        embed.add_field(name="権限", value=role.permissions)
        embed.add_field(name="位置", value=role.position)
        if self.channels[role.guild.id] is not None:
            await self.channels[role.guild.id].send(embed=embed)
    
    # ロール削除
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        embed = discord.Embed(title="🗑️ - ロール削除", 
                              description=f"{role.mention}が削除されました。", 
                              color=discord.Color.red())
        embed.add_field(name="名前", value=role.name)
        embed.add_field(name="ID", value=role.id)
        if self.channels[role.guild.id] is not None:
            await self.channels[role.guild.id].send(embed=embed)
    
    # ロール更新
    @commands.Cog.listener()
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
        embed = discord.Embed(title="🔃 - ロール更新", 
                              description=f"{before.mention}が更新されました。", 
                              color=discord.Color.orange())
        embed.add_field(name="変更前", value=f'名前:{before.name}\n:ID:{before.id}\n色:{before.color}\n権限:{before.permissions}\n位置:{before.position}')
        embed.add_field(name="変更後", value=f'名前:{after.name}\n:ID:{after.id}\n色:{after.color}\n権限:{after.permissions}\n位置:{after.position}')
        if self.channels[before.guild.id] is not None:
            await self.channels[before.guild.id].send(embed=embed)
        
    # チャンネル作成
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: any):
        embed = discord.Embed(title="➕ - チャンネル作成", 
                              description=f"{channel.mention}が作成されました。", 
                              color=discord.Color.green())
        embed.add_field(name="名前", value=channel.name)
        embed.add_field(name="ID", value=channel.id)
        embed.add_field(name="カテゴリ", value=channel.category)
        embed.add_field(name="位置", value=channel.position)
        if self.channels[channel.guild.id] is not None:
            await self.channels[channel.guild.id].send(embed=embed)
    
    # チャンネル削除
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: any):
        embed = discord.Embed(title="🗑️ - チャンネル削除", 
                              description=f"{channel.mention}が削除されました。", 
                              color=discord.Color.red())
        embed.add_field(name="名前", value=channel.name)
        embed.add_field(name="ID", value=channel.id)
        if self.channels[channel.guild.id] is not None:
            await self.channels[channel.guild.id].send(embed=embed)
        
    # チャンネル更新
    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: any, after: any):
        embed = discord.Embed(title="🔃 - チャンネル更新", 
                              description=f"{before.mention}が更新されました。", 
                              color=discord.Color.orange())
        embed.add_field(name="変更前", 
                        value=(f'> 名前\n{before.name}\n' if before.name != after.name else "") + 
                        (f'> カテゴリ\n{before.category}' if before.category != after.category else "") + 
                        (f'> 位置\n{before.position}\n' if before.position != after.position else "") + 
                        (f'> トピック\n{before.topic}' if before.topic != after.topic else ""))
        embed.add_field(name="変更後", value=(f'> 名前\n{after.name}\n' if before.name != after.name else "") + 
                        (f'> カテゴリ\n{after.category}' if before.category != after.category else "") + 
                        (f'> 位置\n{after.position}\n' if before.position != after.position else "") + 
                        (f'> トピック\n{after.topic}' if before.topic != after.topic else ""))
        if self.channels[before.guild.id] is not None:
            await self.channels[before.guild.id].send(embed=embed)
    
    # メンバー参加
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        embed = discord.Embed(title="📥 - メンバー参加", 
                              description=f"{member.mention}が参加しました。", 
                              color=discord.Color.green())
        embed.add_field(name="名前", value=member.name)
        embed.add_field(name="ID", value=member.id)
        embed.add_field(name="アカウント作成日", value=member.created_at)
        if self.channels[member.guild.id] is not None:
            await self.channels[member.guild.id].send(embed=embed)
    
    # メンバー退出
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        embed = discord.Embed(title="📤 - メンバー退出", 
                              description=f"{member.mention}が退出しました。", 
                              color=discord.Color.red())
        embed.add_field(name="名前", value=member.name)
        embed.add_field(name="ID", value=member.id)
        embed.add_field(name="所有していたロール", value=", ".join([role.mention for role in member.roles if role.name != "@everyone"]))
        embed.set_thunmbnail(url=member.avatar.url)
        if self.channels[member.guild.id] is not None:
            await self.channels[member.guild.id].send(embed=embed)
    
    # メンバー更新
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if before.roles != after.roles:
            embed = discord.Embed(title="🔃 - メンバー更新", 
                                  description=f"{before.mention}のロールが更新されました。", 
                                  color=discord.Color.orange())
            embed.add_field(name="追加されたロール", value=" ".join([role.mention for role in after.roles if role not in before.roles]))
            embed.add_field(name="削除されたロール", value=" ".join([role.mention for role in before.roles if role not in after.roles]))
        elif before.nick != after.nick:
            embed = discord.Embed(title="🔃 - メンバー更新", 
                                  description=f"{before.mention}のニックネームが更新されました。", 
                                  color=discord.Color.orange())
            embed.add_field(name="変更前", value=before.nick)
            embed.add_field(name="変更後", value=after.nick if after.nick else f"{after.name} (ニックネームリセット)")
        elif before.is_timed_out != after.is_timed_out:
            if after.timed_out_until is None:
                embed = discord.Embed(title="✅ - メンバーのタイムアウト解除", 
                                      description=f"{before.mention}のタイムアウトが解除されました。", 
                                      color=discord.Color.green())
                embed.add_field(name='名前', value=before.name+"("+before.mention+")")
            else:
                embed = discord.Embed(title="🔇 - メンバーがタイムアウト", 
                                      description=f"{before.mention}がタイムアウトされました。", 
                                      color=discord.Color.red())
                embed.add_field(name='名前', value=f"{before.name} ({before.mention}")
                embed.add_field(name="解除時間", value=f"{discord.utils.format_dt(after.timed_out_until, 'F')}({discord.utils.format_dt(after.timed_out_until, 'R')})")
        else:
            return
        if self.channels[before.guild.id] is not None:
            await self.channels[before.guild.id].send(embed=embed)
        
    
    # いろいろ
    @commands.Cog.listener()
    async def on_audit_log_entry_create(self, entry: discord.AuditLogEntry):
        if entry.action == discord.AuditLogAction.ban:
            embed = discord.Embed(title="🔨 - メンバーをBAN", 
                                  description=f"{entry.target.mention}がBANされました。", 
                                  color=discord.Color.red())
            embed.add_field(name="名前", value=entry.target.name)
            embed.add_field(name="ID", value=entry.target.id)
            embed.add_field(name="理由", value=entry.reason if entry.reason else "特になし")
            embed.add_field(name="BANした人", value=entry.user.mention)
        elif entry.action == discord.AuditLogAction.unban:
            embed = discord.Embed(title="✅ - ユーザーのBANが解除", 
                                  description=f"{entry.target.mention}のBANが解除されました。", 
                                  color=discord.Color.green())
            embed.add_field(name="名前", value=entry.target.name)
            embed.add_field(name="ID", value=entry.target.id)
            embed.add_field(name="理由", value=entry.reason if entry.reason else "特になし")
            embed.add_field(name="BAN解除した人", value=entry.user.mention)
        elif entry.action == discord.AuditLogAction.kick:
            embed = discord.Embed(title="🦶 - メンバーをキック", 
                                  description=f"{entry.target.mention}がキックされました。", 
                                  color=discord.Color.red())
            embed.add_field(name="名前", value=entry.target.name)
            embed.add_field(name="ID", value=entry.target.id)
            embed.add_field(name="理由", value=entry.reason if entry.reason else "特になし")
            embed.add_field(name="キックした人", value=entry.user.mention)
        elif entry.action == discord.AuditLogAction.member_prune:
            embed = discord.Embed(title="🛴 - メンバーのキック", 
                                  description=f"非アクティブメンバーが一括キックされました。", 
                                  color=discord.Color.red())
            embed.add_field(name="キックされたメンバー数", value=entry.extra.members_removed)
            embed.add_field(name="非アクティブ日数", value=entry.reason.delete_members_days)
            embed.add_field(name="キックした人", value=entry.user.mention)
        elif entry.action == discord.AuditLogAction.message_delete:
            embed = discord.Embed(title="🗑️ - メッセージ削除", 
                                  description=f"{entry.target.mention}のメッセージが削除されました。", 
                                  color=discord.Color.red())
            embed.add_field(name="名前", value=entry.target.name)
            embed.add_field(name="ID", value=entry.target.id)
            embed.add_field(name="削除した人", value=entry.user.mention)
        elif entry.action == discord.AuditLogAction.message_bulk_delete:
            embed = discord.Embed(title="🗑️ - メッセージ一括削除", 
                                  description=f"{entry.target.mention}のメッセージが一括削除されました。", 
                                  color=discord.Color.red())
            embed.add_field(name="名前", value=entry.target.name)
            embed.add_field(name="ID", value=entry.target.id)
            embed.add_field(name='チャンネル', value=entry.target.mention)
            embed.add_field(name="削除されたメッセージ数", value=entry.extra.count+"件")
            embed.add_field(name="削除した人", value=entry.user.mention)
        if self.channels[entry.guild.id] is not None:
            await self.channels[entry.guild.id].send(embed=embed)
    
    # 招待の作成
    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite):
        embed = discord.Embed(title="🔗 - 招待リンク作成", 
                              description=f"{invite.inviter.mention}が招待リンクを作成しました。", 
                              color=discord.Color.green())
        embed.add_field(name="招待リンク", value=invite.url)
        embed.add_field(name="最大使用回数", value=invite.max_uses)
        embed.add_field(name="有効期限", value=invite.max_age)
        if self.channels[invite.guild.id] is not None:
            await self.channels[invite.guild.id].send(embed=embed)

    # 招待の削除
    @commands.Cog.listener()
    async def on_invite_delete(self, invite: discord.Invite):
        embed = discord.Embed(title="⛓️‍💥 - 招待リンク削除", 
                              description=f"{invite.inviter.mention}が招待リンクを削除しました。", 
                              color=discord.Color.red())
        embed.add_field(name="招待リンク", value=invite.url)
        if self.channels[invite.guild.id] is not None:
            await self.channels[invite.guild.id].send(embed=embed)
    
    # VC参加/移動/退出
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before: discord.Member, after: discord.Member):
        if before.channel == after.channel:
            return
        if before.channel is None and after.channel is not None:
            embed = discord.Embed(title="🚪 - VC参加", 
                                  description=f"{member.mention}が{after.channel.mention}に参加しました。", 
                                  color=discord.Color.green())
        elif before.channel is not None and after.channel is None:
            embed = discord.Embed(title="🚶‍♂️ - VC退出", 
                                  description=f"{member.mention}が{before.channel.mention}から退出しました。", 
                                  color=discord.Color.red())
        else:
            embed = discord.Embed(title="🚶‍♂️‍➡️ - VC移動", 
                                  description=f"{member.mention}が{before.channel.mention}から{after.channel.mention}に移動しました。", 
                                  color=discord.Color.blurple())
        if self.channels[member.guild.id] is not None:
            await self.channels[member.guild.id].send(embed=embed)
    
    
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(logger(bot))