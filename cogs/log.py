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
    
    # チャンネル更新
    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
        if before.name == after.name and before.topic == after.topic:
            return
        embed = discord.Embed(title="🔃 - チャンネル更新", 
                              description=f"{before.mention}が更新されました。", 
                              color=discord.Color.orange())
        embed.add_field(name="変更前", value=(f'> 名前\n{before.name}\n' if before.name != after.name else "") +
                        
                        (f'> トピック\n{before.topic}' if before.topic != after.topic else ""))
        embed.add_field(name="変更後", value=(f'> 名前\n{after.name}\n' if before.name != after.name else "") + (f'> トピック\n{after.topic}' if before.topic != after.topic else ""))
        async for entry in before.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_update):
            embed.add_field(name="変更した人", value=entry.user.mention)
        if self.channels[before.guild.id] is not None:
            await self.channels[before.guild.id].send(embed=embed)
    
    # チャンネル削除
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        embed = discord.Embed(title="🗑️ - チャンネル削除", 
                              description=f"{channel.mention}が削除されました。", 
                              color=discord.Color.red())
        embed.add_field(name="名前", value=channel.name)
        embed.add_field(name="ID", value=channel.id)
        async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
            embed.add_field(name="削除した人", value=entry.user.mention)
        if self.channels[channel.guild.id] is not None:
            await self.channels[channel.guild.id].send(embed=embed)
    
    
    # メンバー参加
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        embed = discord.Embed(title="📥 - メンバー参加", 
                              description=f"{member.mention}が参加しました。", 
                              color=discord.Color.green())
        embed.add_field(name="名前", value=member.name)
        embed.add_field(name="ID", value=member.id)
        embed.add_field(name="アカウント作成日", value=member.created_at)
        embed.add_field(name="現在のサーバー人数", value=f"{member.guild.member_count}人")
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
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
        embed.set_thunmbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        if self.channels[member.guild.id] is not None:
            await self.channels[member.guild.id].send(embed=embed)
        
    
    # いろいろ
    @commands.Cog.listener()
    async def on_audit_log_entry_create(self, entry: discord.AuditLogEntry):
        # IMPORTANT:Discord.py開発者さん改良してください。お願いします。マジでコード短くしてくださいお願いします。ObjectじゃなくてUserを返してください。
        # BAN
        if entry.action == discord.AuditLogAction.ban:
            if type(entry.target) == discord.Member:
                embed = discord.Embed(title="🔨 - メンバーをBAN", 
                                    description=f"{entry.target.mention}がBANされました。", 
                                    color=discord.Color.red())
                embed.add_field(name="名前", value=entry.target.name)
                embed.add_field(name="ID", value=entry.target.id)
                embed.add_field(name="理由", value=entry.reason if entry.reason else "特になし")
                embed.add_field(name="BANした人", value=entry.user.mention)
                embed.set_thumbnail(url=entry.target.avatar.url if entry.target.avatar.url else entry.target.default_avatar.url)

            else:
                m = await self.bot.fetch_user(entry.target.id)
                embed = discord.Embed(title="🔨 - ユーザーをBAN", 
                                    description=f"{m.mention}がBANされました。", 
                                    color=discord.Color.red())
                embed.add_field(name="名前", value=m.name)
                embed.add_field(name="ID", value=m.id)
                embed.add_field(name="理由", value=entry.reason if entry.reason else "特になし")
                embed.add_field(name="BANした人", value=entry.user.mention)
                embed.set_thumbnail(url=m.avatar.url)

        # BAN解除
        elif entry.action == discord.AuditLogAction.unban:
            if type(entry.target) == discord.Member:
                embed = discord.Embed(title="✅ - メンバーのBANが解除", 
                                    description=f"{entry.target.mention}のBANが解除されました。", 
                                    color=discord.Color.green())
                embed.add_field(name="名前", value=entry.target.name)
                embed.add_field(name="ID", value=entry.target.id)
                embed.add_field(name="理由", value=entry.reason if entry.reason else "特になし")
                embed.add_field(name="BAN解除した人", value=entry.user.mention)

            else:
                m = await self.bot.fetch_user(entry.target.id)
                embed = discord.Embed(title="✅ - ユーザーのBANが解除", 
                                      description=f"{m.mention}のBANが解除されました。",
                                        color=discord.Color.green())
                embed.add_field(name="名前", value=m.name)
                embed.add_field(name="ID", value=m.id)
                embed.add_field(name="理由", value=entry.reason if entry.reason else "特になし")
                embed.add_field(name="BAN解除した人", value=entry.user.mention)
                
        # Kick
        elif entry.action == discord.AuditLogAction.kick:
            if type(entry.target) == discord.Member:
                embed = discord.Embed(title="🦶 - メンバーをキック", 
                                  description=f"{entry.target.mention}がキックされました。", 
                                  color=discord.Color.red())
                embed.add_field(name="名前", value=entry.target.name)
                embed.add_field(name="ID", value=entry.target.id)
                embed.add_field(name="理由", value=entry.reason if entry.reason else "特になし")
                embed.add_field(name="キックした人", value=entry.user.mention)

            else:
                m = await self.bot.fetch_user(entry.target.id)
                embed = discord.Embed(title="🦶 - ユーザーをキック", 
                                  description=f"{m.mention}がキックされました。", 
                                  color=discord.Color.red())
                embed.add_field(name="名前", value=m.name)
                embed.add_field(name="ID", value=m.id)
                embed.add_field(name="理由", value=entry.reason if entry.reason else "特になし")
                embed.add_field(name="キックした人", value=entry.user.mention)
                
        # 非アクティブメンバーキック
        elif entry.action == discord.AuditLogAction.member_prune:
            embed = discord.Embed(title="🛴 - メンバーのキック", 
                                  description=f"非アクティブメンバーが一括キックされました。", 
                                  color=discord.Color.red())
            embed.add_field(name="キックされたメンバー数", value=entry.extra.members_removed)
            embed.add_field(name="非アクティブ日数", value=entry.reason.delete_members_days)
            embed.add_field(name="キックした人", value=entry.user.mention)
        
        # メッセージ削除
        elif entry.action == discord.AuditLogAction.message_delete:
            embed = discord.Embed(title="🗑️ - メッセージ削除", 
                                  description=f"{entry.target.mention}のメッセージが削除されました。", 
                                  color=discord.Color.red())
            embed.add_field(name="名前", value=entry.target.name)
            embed.add_field(name="ID", value=entry.target.id)
            embed.add_field(name="削除した人", value=entry.user.mention)
        
        # メッセージ一括削除
        elif entry.action == discord.AuditLogAction.message_bulk_delete:
            if type(entry.target) != discord.TextChannel:
                embed = discord.Embed(title="🗑️ - メッセージ一括削除", 
                                    description=f"{entry.target.mention}のメッセージが一括削除されました。", 
                                    color=discord.Color.red())
                embed.add_field(name='チャンネル', value=entry.target.mention)
                embed.add_field(name="削除されたメッセージ数", value=f"{entry.extra.count}件")
                embed.add_field(name="削除した人", value=entry.user.mention)

            else:
                ch = await self.bot.fetch_channel(entry.target.id)
                embed = discord.Embed(title="🗑️ - メッセージ一括削除",
                                    description=f"{ch.mention}のメッセージが一括削除されました。",
                                    color=discord.Color.red())
                embed.add_field(name="削除されたメッセージ数", value=f"{entry.extra.count}件")
                embed.add_field(name="削除した人", value=entry.user.mention)    
        
        # チャンネル作成
        elif entry.action == discord.AuditLogAction.channel_create:
            embed = discord.Embed(title="➕ - チャンネル作成", 
                                  description=f"{entry.target.mention}が作成されました。", 
                                  color=discord.Color.green())
            embed.add_field(name="名前", value=entry.target.name)
            embed.add_field(name="ID", value=entry.target.id)
            embed.add_field(name="カテゴリ", value=entry.target.category)
            embed.add_field(name="位置", value=entry.target.position)
            embed.add_field(name="作成した人", value=entry.user.mention)

        # チャンネル削除
        elif entry.action == discord.AuditLogAction.channel_delete:
            embed = discord.Embed(title="🗑️ - チャンネル削除", 
                                  description=f"{entry.target.mention}が削除されました。", 
                                  color=discord.Color.red())
            embed.add_field(name="名前", value=entry.target.name)
            embed.add_field(name="ID", value=entry.target.id)
            embed.add_field(name="削除した人", value=entry.user.mention)
        
        # ロール作成
        elif entry.action == discord.AuditLogAction.role_create:
            embed = discord.Embed(title="➕ - ロール作成", 
                                  description=f"{entry.target.mention}が作成されました。", 
                                  color=discord.Color.green())
            embed.add_field(name="名前", value=entry.target.name)
            embed.add_field(name="ID", value=entry.target.id)
            embed.add_field(name="色", value=entry.target.color)
            embed.add_field(name="権限", value=entry.target.permissions)
            embed.add_field(name="位置", value=entry.target.position)
            embed.add_field(name="作成した人", value=entry.user.mention)
            
        # ロール削除
        elif entry.action == discord.AuditLogAction.role_delete:
            embed = discord.Embed(title="🗑️ - ロール削除", 
                                  description=f"{entry.target.mention}が削除されました。", 
                                  color=discord.Color.red())
            embed.add_field(name="名前", value=entry.target.name)
            embed.add_field(name="ID", value=entry.target.id)
            embed.add_field(name="削除した人", value=entry.user.mention)
            
        # ロール更新
        elif entry.action == discord.AuditLogAction.role_update:
            embed = discord.Embed(title="🔃 - ロール更新", 
                                  description=f"{entry.before.mention}が更新されました。", 
                                  color=discord.Color.orange())
            embed.add_field(name="変更前",
                            value=(f'> 名前\n{entry.after.name}\n' if entry.before.name != entry.after.name else "") + 
                            (f'> 色\n{entry.after.color}' if entry.before.color != entry.after.color else "") +  
                            (f'> 絵文字\n{entry.after.unicode_emoji}' if entry.before.unicode_emoji != entry.after.unicode_emoji else "") +
                            (f'> 位置\n{entry.after.position}' if entry.before.position != entry.after.position else "") + 
                            (f'> 権限\n{entry.after.permissions}' if entry.before.permissions != entry.after.permissions else ""))
            embed.add_field(name="変更後", 
                            value=(f'> 名前\n{entry.after.name}\n' if entry.before.name != entry.after.name else "") + 
                            (f'> 色\n{entry.after.color}' if entry.before.color != entry.after.color else "") +  
                            (f'> 絵文字\n{entry.after.unicode_emoji}' if entry.before.unicode_emoji != entry.after.unicode_emoji else "") + 
                            (f'> 位置\n{entry.after.position}' if entry.before.position != entry.after.position else "") +
                            (f'> 権限\n{entry.after.permissions}' if entry.before.permissions != entry.after.permissions else ""))
            embed.add_field(name="変更した人", value=entry.user.mention)
            
        # 招待作成
        elif entry.action == discord.AuditLogAction.invite_create:
            embed = discord.Embed(title="🔗 - 招待リンク作成", 
                                  description=f"{entry.user.mention}が招待リンクを作成しました。", 
                                  color=discord.Color.green())
            embed.add_field(name="招待リンク", value=entry.target.url)
            embed.add_field(name="最大使用回数", value=entry.target.max_uses)
            embed.add_field(name="有効期限", value=entry.target.max_age)
            embed.add_field(name="作成した人", value=entry.user.mention)
        
        # 招待削除
        elif entry.action == discord.AuditLogAction.invite_delete:
            embed = discord.Embed(title="⛓️‍💥 - 招待リンク削除", 
                                  description=f"{entry.user.mention}が招待リンクを削除しました。", 
                                  color=discord.Color.red())
            embed.add_field(name="招待リンク", value=entry.target.url)
            embed.add_field(name="削除した人", value=entry.user.mention)
        
        # メンバーロール更新
        elif entry.action == discord.AuditLogAction.member_role_update:
            embed = discord.Embed(title="🔃 - メンバーロール更新", 
                                  description=f"{entry.target.mention}のロールが更新されました。", 
                                  color=discord.Color.orange())
            embed.add_field(name="追加されたロール", value=" ".join([role.mention for role in entry.after.roles if role not in entry.before.roles]))
            embed.add_field(name="削除されたロール", value=" ".join([role.mention for role in entry.before.roles if role not in entry.after.roles]))
            embed.add_field(name="変更した人", value=entry.user.mention)
        
        # メンバー更新
        elif entry.action == discord.AuditLogAction.member_update:
            # ニックネーム変更
            if type(entry.target) == discord.Member:
                if entry.before.nick != entry.after.nick:
                    embed = discord.Embed(title="🔃 - メンバー更新", 
                                    description=f"{entry.target.mention}のニックネームが更新されました。", 
                                    color=discord.Color.orange())
                    embed.add_field(name="変更前", value=entry.before.nick)
                    embed.add_field(name="変更後", value=entry.after.nick if entry.after.nick else f"{entry.after.name} (ニックネームリセット)")
                    embed.add_field(name="変更した人", value=entry.user.mention)
                # タイムアウト
            elif entry.before.is_timed_out() != entry.after.is_timed_out():
                if entry.after.timed_out_until is None:
                    embed = discord.Embed(title="✅ - メンバーのタイムアウト解除", 
                                    description=f"{entry.target.mention}のタイムアウトが解除されました。", 
                                    color=discord.Color.green())
                    embed.add_field(name='名前', value=entry.target.name+"("+entry.target.mention+")")
                else:
                    embed = discord.Embed(title="🔇 - メンバーがタイムアウト", 
                                    description=f"{entry.target.mention}がタイムアウトされました。", 
                                    color=discord.Color.red())
                    embed.add_field(name='名前', value=f"{entry.target.name} ({entry.target.mention}")
                    embed.add_field(name="解除時間", value=f"{discord.utils.format_dt(entry.after.timed_out_until, 'F')}({discord.utils.format_dt(entry.after.timed_out_until, 'R')})")
                
        else:
            return
        if self.channels[entry.guild.id] is not None:
            await self.channels[entry.guild.id].send(embed=embed)
    
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