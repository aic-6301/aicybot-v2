import discord
from discord.ext import commands, tasks
from discord import app_commands

from utils import database
from utils.locale import t

class logger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # メッセージ編集
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot or before.guild is None:
            return
        if before.content == after.content:
            return
        embed = discord.Embed(title = t(before.guild.preferred_locale.value, "log.message_edit"), 
                              description = t(before.guild.preferred_locale.value, "log.message_edit_description", author=before.author.mention), 
                              color = discord.Color.orange())
        embed.add_field(name = t(before.guild.preferred_locale.value, "log.before"), value = before.content)
        embed.add_field(name = t(before.guild.preferred_locale.value, "log.after"), value = after.content)
        embed.add_field(name = t(before.guild.preferred_locale.value, "log.message_link"), value = after.jump_url, inline = False)
        embed.add_field(name = t(before.guild.preferred_locale.value, "log.channel"), value = before.channel.mention, inline = False)
        if database.get('settings', before.guild.id)[1] is not None:
            await self.bot.get_channel(database.get('settings', before.guild.id)[1]).send(embed = embed)

    # メッセージ削除
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Role):
        if message.author.bot or message.guild is None:
            return
        embed = discord.Embed(title = t(message.guild.preferred_locale.value, "log.message_delete"), 
                              description = t(message.guild.preferred_locale.value, "log.message_delete_description", author=message.author.mention), 
                              color = discord.Color.red())
        embed.add_field(name = t(message.guild.preferred_locale.value, "log.content"), value = message.content)
        embed.add_field(name = t(message.guild.preferred_locale.value, "log.channel"), value = message.channel.mention)
        if database.get('settings', message.guild.id)[1] is not None:
            await self.bot.get_channel(database.get('settings', message.guild.id)[1]).send(embed = embed)

    # チャンネル更新
    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
        if before.type == discord.ChannelType.text:
            if before.name != after.name:
                before_name = f"{t(before.guild.preferred_locale.value, 'log.name')}\n{before.name}\n"
                after_name = f"{t(after.guild.preferred_locale.value, 'log.name')}\n{after.name}\n"
            else:
                before_name = None
                after_name = None
            if before.topic != after.topic and before.topic is not None and after.topic is not None:
                before_topic = f"{t(before.guild.preferred_locale.value, 'log.topic')}\n{before.topic}"
                after_topic = f"{t(after.guild.preferred_locale.value, 'log.topic')}\n{after.topic}"
            else:
                before_topic = None
                after_topic = None
            before_topic = None
            after_topic = None
        else:
            if before.name != after.name:
                before_name = f"{t(before.guild.preferred_locale.value, 'log.name')}\n{before.name}\n"
                after_name = f"{t(after.guild.preferred_locale.value, 'log.name')}\n{after.name}\n"
            else:
                before_name = None
                after_name = None
        if before_topic is None and before_name is None:
            return
        embed = discord.Embed(title = t(before.guild.preferred_locale.value, "log.channel_update"), 
                              description = f"{before.mention}が更新されました。", 
                              color = discord.Color.orange())
        embed.add_field(name = t(before.guild.preferred_locale.value, "log.before"), value = (before_name + before_topic))
        embed.add_field(name = t(before.guild.preferred_locale.value, "log.after"), value = (after_name + after_topic))
        async for entry in before.guild.audit_logs(limit = 1, action = discord.AuditLogAction.channel_update):
            embed.add_field(name = t(before.guild.preferred_locale.value, "log.changed_by"), value = entry.user.mention)
        if database.get('settings', before.guild.id)[1] is not None:
            await self.bot.get_channel(database.get('settings', before.guild.id)[1]).send(embed = embed)

    # チャンネル削除
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        embed = discord.Embed(title = t(channel.guild.preferred_locale.value, "log.channel_delete"), 
                              description = f"{channel.mention}が削除されました。", 
                              color = discord.Color.red())
        embed.add_field(name = t(channel.guild.preferred_locale.value, "log.name"), value = channel.name)
        embed.add_field(name = t(channel.guild.preferred_locale.value, "log.id"), value = channel.id)
        async for entry in channel.guild.audit_logs(limit = 1, action = discord.AuditLogAction.channel_delete):
            embed.add_field(name = t(channel.guild.preferred_locale.value, "log.deleted_by"), value = entry.user.mention)
        if database.get('settings', channel.guild.id)[1] is not None:
            await self.bot.get_channel(database.get('settings', channel.guild.id)[1]).send(embed = embed)

    # メンバー参加
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        embed = discord.Embed(title = t(member.guild.preferred_locale.value, "log.member_join"), 
                              description = t(member.guild.preferred_locale.value, "log.member_join_description", member=member.mention), 
                              color = discord.Color.green())
        embed.add_field(name = t(member.guild.preferred_locale.value, "member.name"), value = member.name)
        embed.add_field(name = t(member.guild.preferred_locale.value, "member.id"), value = member.id)
        embed.add_field(name = t(member.guild.preferred_locale.value, "member.created_at"), value = member.created_at)
        embed.add_field(name = t(member.guild.preferred_locale.value, "log.current_member_count"), value = f"{member.guild.member_count}人")
        embed.set_thumbnail(url = member.avatar.url if member.avatar else member.default_avatar.url)
        if database.get('settings', member.guild.id)[1] is not None:
            await self.bot.get_channel(database.get('settings', member.guild.id)[1]).send(embed = embed)

    # メンバー退出
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        embed = discord.Embed(title = t(member.guild.preferred_locale.value, "log.member_remove"), 
                              description = t(member.guild.preferred_locale.value, "log.member_remove_description", member=member.mention), 
                              color = discord.Color.red())
        embed.add_field(name = t(member.guild.preferred_locale.value, "member.name"), value = member.name)
        embed.add_field(name = t(member.guild.preferred_locale.value, "member.id"), value = member.id)
        embed.add_field(name = t(member.guild.preferred_locale.value, "log.had_role"), value = ", ".join([role.mention for role in member.roles if role.name != "@everyone"]))
        embed.set_thumbnail(url = member.avatar.url if member.avatar else member.default_avatar.url)
        if database.get('settings', member.guild.id)[1] is not None:
            await self.bot.get_channel(database.get('settings', member.guild.id)[1]).send(embed = embed)
            
    # ロール更新
    @commands.Cog.listener()
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
        embed = discord.Embed(title = t(before.guild.preferred_locale.value, "log.role_update"),
                              description = t(before.guild.preferred_locale.value, "log.role_update_description", role=before.mention),
                              color = discord.Color.orange())
        embed.add_field(name = t(before.guild.preferred_locale.value, "log.before"), value = (f'> {t(before.guild.preferred_locale.value, "log.name")}\n{after.name}\n' if before.name and before.name != after.name else "") + 
                            (f'> {t(before.guild.preferred_locale.value, "log.color")}\n{after.color}' if before.color and before.color != after.color else "") +  
                            (f'> {t(before.guild.preferred_locale.value, "log.emoji")}\n{after.unicode_emoji}' if before.unicode_emoji and before.unicode_emoji != after.unicode_emoji else "") +
                            (f'> {t(before.guild.preferred_locale.value, "log.position")}\n{after.position}' if before.position and before.position != after.position else "") + 
                            (f'> {t(before.guild.preferred_locale.value, "log.permissions")}\n{after.permissions}' if before.permissions and before.permissions != after.permissions else ""))
        embed.add_field(name = t(before.guild.preferred_locale.value, "log.after"), value = (f'> {t(before.guild.preferred_locale.value, "log.name")}\n{after.name}\n' if before.name and before.name != after.name else "") + 
                            (f'> {t(before.guild.preferred_locale.value, "log.color")}\n{after.color}' if before.color and before.color != after.color else "") +  
                            (f'> {t(before.guild.preferred_locale.value, "log.emoji")}\n{after.unicode_emoji}' if before.unicode_emoji and before.unicode_emoji != after.unicode_emoji else "") +
                            (f'> {t(before.guild.preferred_locale.value, "log.position")}\n{after.position}' if before.position and before.position != after.position else "") + 
                            (f'> {t(before.guild.preferred_locale.value, "log.permissions")}\n{after.permissions}' if before.permissions and before.permissions != after.permissions else ""))
        async for entry in before.guild.audit_logs(limit = 1, action = discord.AuditLogAction.role_update):
            embed.add_field(name = t(before.guild.preferred_locale.value, "log.updated_by"), value = entry.user.mention)
        if database.get('settings', before.guild.id)[1] is not None:
            await self.bot.get_channel(database.get('settings', before.guild.id)[1]).send(embed = embed)
        
    
    # いろいろ
    @commands.Cog.listener()
    async def on_audit_log_entry_create(self, entry: discord.AuditLogEntry):
        # IMPORTANT:Discord.py開発者さん改良してください。お願いします。マジでコード短くしてくださいお願いします。ObjectじゃなくてUserを返してください。
        # BAN
        if entry.action == discord.AuditLogAction.ban:
            if type(entry.target) == discord.Member:
                embed = discord.Embed(title = t(entry.guild.preferred_locale.value, "log.banned"), 
                                    description = t(entry.guild.preferred_locale.value, "log.banned_description", user=entry.target.mention), 
                                    color = discord.Color.red())
                embed.add_field(name = t(entry.guild.preferred_locale.value, "log.name"), value = entry.target.name)
                embed.add_field(name = t(entry.guild.preferred_locale.value, "log.id"), value = entry.target.id)
                embed.add_field(name = t(entry.guild.preferred_locale.value, "log.reason"), value = entry.reason if entry.reason else t(entry.guild.preferred_locale.value, "log.no_reason"))
                embed.add_field(name = t(entry.guild.preferred_locale.value, "log.banned_by"), value = entry.user.mention)
                embed.set_thumbnail(url = entry.target.avatar.url if entry.target.avatar.url else entry.target.default_avatar.url)

            else:
                m = await self.bot.fetch_user(entry.target.id)
                embed = discord.Embed(title = t(entry.guild.preferred_locale.value, "log.banned"), 
                                    description = t(entry.guild.preferred_locale.value, "log.banned_description", user=m.mention), 
                                    color = discord.Color.red())
                embed.add_field(name = t(entry.guild.preferred_locale.value, "log.name"), value = m.name)
                embed.add_field(name = t(entry.guild.preferred_locale.value, "log.id"), value = m.id)
                embed.add_field(name = t(entry.guild.preferred_locale.value, "log.reason"), value = entry.reason if entry.reason else t(entry.guild.preferred_locale.value, "log.no_reason"))
                embed.add_field(name = t(entry.guild.preferred_locale.value, "log.banned_by"), value = entry.user.mention)
                embed.set_thumbnail(url = m.avatar.url)

        # BAN解除
        elif entry.action == discord.AuditLogAction.unban:
            if type(entry.target) == discord.Member:
                embed = discord.Embed(title = t(entry.guild.preferred_locale.value, "log.unbanned"), 
                                    description = t(entry.guild.preferred_locale.value, "log.unbanned_description", user=entry.target.mention), 
                                    color = discord.Color.green())
                embed.add_field(name = t(entry.guild.preferred_locale.value, "log.name"), value = entry.target.name)
                embed.add_field(name = t(entry.guild.preferred_locale.value, "log.id"), value = entry.target.id)
                embed.add_field(name = t(entry.guild.preferred_locale.value, "log.reason"), value = entry.reason if entry.reason else t(entry.guild.preferred_locale.value, "log.no_reason"))
                embed.add_field(name = t(entry.guild.preferred_locale.value, "log.banned_by"), value = entry.user.mention)

            else:
                m = await self.bot.fetch_user(entry.target.id)
                embed = discord.Embed(title = t(entry.guild.preferred_locale.value, "log.unbanned"),
                                      description = t(entry.guild.preferred_locale.value, "log.unbanned_description", user=m.mention), 
                                      color = discord.Color.green())
                embed.add_field(name = t(entry.guild.preferred_locale.value, "log.name"), value = m.name)
                embed.add_field(name = t(entry.guild.preferred_locale.value, "log.id"), value = m.id)
                embed.add_field(name = t(entry.guild.preferred_locale.value, "log.reason"), value = entry.reason if entry.reason else t(entry.guild.preferred_locale.value, "log.no_reason"))
                embed.add_field(name = t(entry.guild.preferred_locale.value, "log.banned_by"), value = entry.user.mention)

        # Kick
        elif entry.action == discord.AuditLogAction.kick:
            if type(entry.target) == discord.Member:
                embed = discord.Embed(title = t(entry.guild.preferred_locale.value, "log.kicked"),
                                  description = t(entry.guild.preferred_locale.value, "log.kicked_description", user=entry.target.mention),
                                  color = discord.Color.red())
                embed.add_field(name = t(entry.guild.preferred_locale.value, "log.name"), value = entry.target.name)
                embed.add_field(name = t(entry.guild.preferred_locale.value, "log.id"), value = entry.target.id)
                embed.add_field(name = t(entry.guild.preferred_locale.value, "log.reason"), value = entry.reason if entry.reason else t(entry.guild.preferred_locale.value, "log.no_reason"))
                embed.add_field(name = t(entry.guild.preferred_locale.value, "log.kicked_by"), value = entry.user.mention)

            else:
                m = await self.bot.fetch_user(entry.target.id)
                embed = discord.Embed(title = t(entry.guild.preferred_locale.value, "log.kicked"),
                                      description = t(entry.guild.preferred_locale.value, "log.kicked_description", user=m.mention),
                                      color = discord.Color.red())
                embed.add_field(name = t(entry.guild.preferred_locale.value, "log.name"), value = m.name)
                embed.add_field(name = t(entry.guild.preferred_locale.value, "log.id"), value = m.id)
                embed.add_field(name = t(entry.guild.preferred_locale.value, "log.reason"), value = entry.reason if entry.reason else t(entry.guild.preferred_locale.value, "log.no_reason"))
                embed.add_field(name = t(entry.guild.preferred_locale.value, "log.kicked_by"), value = entry.user.mention)
                
        # 非アクティブメンバーキック
        elif entry.action == discord.AuditLogAction.member_prune:
            embed = discord.Embed(title = t(entry.guild.preferred_locale.value, "log.member_prune"),
                                  description = t(entry.guild.preferred_locale.value, "log.member_prune_description"),
                                  color = discord.Color.red())
            embed.add_field(name = t(entry.guild.preferred_locale.value, "log.kicked_members"), value = entry.extra.members_removed)
            embed.add_field(name = t(entry.guild.preferred_locale.value, "log.inactive_days"), value = entry.reason.delete_members_days)
            embed.add_field(name = t(entry.guild.preferred_locale.value, "log.kicked_by"), value = entry.user.mention)

        # メッセージ削除
        elif entry.action == discord.AuditLogAction.message_delete:
            embed = discord.Embed(title = t(entry.guild.preferred_locale.value, "log.message_delete"),
                                  description = t(entry.guild.preferred_locale.value, "log.message_deleted_description", user=entry.target.mention),
                                  color = discord.Color.red())
            embed.add_field(name = t(entry.guild.preferred_locale.value, "log.name"), value = entry.target.name)
            embed.add_field(name = t(entry.guild.preferred_locale.value, "log.id"), value = entry.target.id)
            embed.add_field(name = t(entry.guild.preferred_locale.value, "log.deleted_by"), value = entry.user.mention)

        # メッセージ一括削除
        elif entry.action == discord.AuditLogAction.message_bulk_delete:
            if type(entry.target) != discord.TextChannel:
                embed = discord.Embed(title = t(entry.guild.preferred_locale.value, "log.bulk_deleted"),
                                    description = t(entry.guild.preferred_locale.value, "log.bulk_deleted_description", channel=entry.target.mention),
                                    color = discord.Color.red())
                embed.add_field(name = t(entry.guild.preferred_locale.value, "log.channel"), value = entry.target.mention)
                embed.add_field(name = t(entry.guild.preferred_locale.value, "log.bulk_deleted_count"), value = f"{entry.extra.count}件")
                embed.add_field(name = t(entry.guild.preferred_locale.value, "log.deleted_by"), value = entry.user.mention)

            else:
                ch = await self.bot.fetch_channel(entry.target.id)
                embed = discord.Embed(title = t(entry.guild.preferred_locale.value, "log.bulk_deleted"),
                                    description = t(entry.guild.preferred_locale.value, "log.bulk_deleted_description", channel=ch.mention),
                                    color = discord.Color.red())
                embed.add_field(name = t(entry.guild.preferred_locale.value, "log.bulk_deleted_count"), value = f"{entry.extra.count}件")
                embed.add_field(name = t(entry.guild.preferred_locale.value, "log.deleted_by"), value = entry.user.mention)

        # チャンネル作成
        elif entry.action == discord.AuditLogAction.channel_create:
            embed = discord.Embed(title = t(entry.guild.preferred_locale.value, "log.channel_create"),
                                  description = t(entry.guild.preferred_locale.value, "log.channel_created_description", user=entry.target.mention),
                                  color = discord.Color.green())
            embed.add_field(name = t(entry.guild.preferred_locale.value, "log.name"), value = entry.target.name)
            embed.add_field(name = t(entry.guild.preferred_locale.value, "log.id"), value = entry.target.id)
            embed.add_field(name = t(entry.guild.preferred_locale.value, "log.category"), value = entry.target.category)
            embed.add_field(name = t(entry.guild.preferred_locale.value, "log.position"), value = entry.target.position)
            embed.add_field(name = t(entry.guild.preferred_locale.value, "log.created_by"), value = entry.user.mention)

        # チャンネル削除
        elif entry.action == discord.AuditLogAction.channel_delete:
            embed = discord.Embed(title = t(entry.guild.preferred_locale.value, "log.channel_delete"),
                                  description = t(entry.guild.preferred_locale.value, "log.channel_deleted_description", channel=entry.target.mention),
                                  color = discord.Color.red())
            embed.add_field(name = t(entry.guild.preferred_locale.value, "log.name"), value = entry.target.name)
            embed.add_field(name = t(entry.guild.preferred_locale.value, "log.id"), value = entry.target.id)
            embed.add_field(name = t(entry.guild.preferred_locale.value, "log.deleted_by"), value = entry.user.mention)

        # ロール作成
        elif entry.action == discord.AuditLogAction.role_create:
            embed = discord.Embed(title = t(entry.guild.preferred_locale.value, "log.role_create"),
                                  description = t(entry.guild.preferred_locale.value, "log.role_created_description", role=entry.target.mention),
                                  color = discord.Color.green())
            embed.add_field(name = t(entry.guild.preferred_locale.value, "log.name"), value = entry.target.name)
            embed.add_field(name = t(entry.guild.preferred_locale.value, "log.id"), value = entry.target.id)
            embed.add_field(name = t(entry.guild.preferred_locale.value, "log.color"), value = entry.target.color)
            embed.add_field(name = t(entry.guild.preferred_locale.value, "log.permissions"), value = entry.target.permissions)
            embed.add_field(name = t(entry.guild.preferred_locale.value, "log.position"), value = entry.target.position)
            embed.add_field(name = t(entry.guild.preferred_locale.value, "log.created_by"), value = entry.user.mention)

        # ロール削除
        elif entry.action == discord.AuditLogAction.role_delete:
            embed = discord.Embed(title = t(entry.guild.preferred_locale.value, "log.role_delete"),
                                  description = t(entry.guild.preferred_locale.value, "log.role_deleted_description", role=entry.target.mention),
                                  color = discord.Color.red())
            embed.add_field(name = t(entry.guild.preferred_locale.value, "log.name"), value = entry.target.name)
            embed.add_field(name = t(entry.guild.preferred_locale.value, "log.id"), value = entry.target.id)
            embed.add_field(name = t(entry.guild.preferred_locale.value, "log.deleted_by"), value = entry.user.mention)

        # 招待作成
        elif entry.action == discord.AuditLogAction.invite_create:
            embed = discord.Embed(title = t(entry.guild.preferred_locale.value, "log.invite_create"),
                                  description = t(entry.guild.preferred_locale.value, "log.invite_created_description", user=entry.user.mention),
                                  color = discord.Color.green())
            embed.add_field(name = t(entry.guild.preferred_locale.value, "log.invite_link"), value = entry.target.url)
            embed.add_field(name = t(entry.guild.preferred_locale.value, "log.max_uses"), value = entry.target.max_uses)
            embed.add_field(name = t(entry.guild.preferred_locale.value, "log.max_age"), value = entry.target.max_age)
            embed.add_field(name = t(entry.guild.preferred_locale.value, "log.created_by"), value = entry.user.mention)
        
        # 招待削除
        elif entry.action == discord.AuditLogAction.invite_delete:
            embed = discord.Embed(title = t(entry.guild.preferred_locale.value, "log.invite_delete"),
                                  description = t(entry.guild.preferred_locale.value, "log.invite_deleted_description", user=entry.user.mention),
                                  color = discord.Color.red())
            embed.add_field(name = t(entry.guild.preferred_locale.value, "log.invite_link"), value = entry.target.url)
            embed.add_field(name = t(entry.guild.preferred_locale.value, "log.deleted_by"), value = entry.user.mention)

        # メンバーロール更新
        elif entry.action == discord.AuditLogAction.member_role_update:
            embed = discord.Embed(title = t(entry.guild.preferred_locale.value, "log.member_role_update"),
                                  description = t(entry.guild.preferred_locale.value, "log.member_role_updated_description", user=entry.target.mention),
                                  color = discord.Color.orange())
            embed.add_field(name = t(entry.guild.preferred_locale.value, "log.added_roles"), value = " ".join([role.mention for role in entry.after.roles if role not in entry.before.roles]))
            embed.add_field(name = t(entry.guild.preferred_locale.value, "log.removed_roles"), value = " ".join([role.mention for role in entry.before.roles if role not in entry.after.roles]))
            embed.add_field(name = t(entry.guild.preferred_locale.value, "log.changed_by"), value = entry.user.mention)

        # メンバー更新
        elif entry.action == discord.AuditLogAction.member_update:
            # ニックネーム変更
            if type(entry.target) == discord.Member:
                if entry.before.nick != entry.after.nick:
                    embed = discord.Embed(title = t(entry.guild.preferred_locale.value, "log.member_update"),
                                    description = t(entry.guild.preferred_locale.value, "log.member_nick_update_description", user=entry.target.mention),
                                    color = discord.Color.orange())
                    embed.add_field(name = t(entry.guild.preferred_locale.value, "log.before_change"), value = entry.before.nick)
                    embed.add_field(name = t(entry.guild.preferred_locale.value, "log.after_change"), value = entry.after.nick if entry.after.nick else f"{entry.after.name} (ニックネームリセット)")
                    embed.add_field(name = t(entry.guild.preferred_locale.value, "log.changed_by"), value = entry.user.mention)
                # タイムアウト
            elif entry.before.is_timed_out() != entry.after.is_timed_out():
                if entry.after.timed_out_until is None:
                    embed = discord.Embed(title = t(entry.guild.preferred_locale.value, "log.untimed_out"),
                                    description = t(entry.guild.preferred_locale.value, "log.untimed_out_description", user=entry.target.mention),
                                    color = discord.Color.green())
                    embed.add_field(name = t(entry.guild.preferred_locale.value, "log.name"), value = entry.target.name+"("+entry.target.mention+")")
                else:
                    embed = discord.Embed(title = t(entry.guild.preferred_locale.value, "log.member_timed_out"),
                                    description = t(entry.guild.preferred_locale.value, "log.member_timed_out_description", user=entry.target.mention),
                                    color = discord.Color.red())
                    embed.add_field(name = t(entry.guild.preferred_locale.value, "log.name"), value = f"{entry.target.name} ({entry.target.mention})")
                    embed.add_field(name = t(entry.guild.preferred_locale.value, "log.time_out_duration"), value = f"{discord.utils.format_dt(entry.after.timed_out_until, 'F')}({discord.utils.format_dt(entry.after.timed_out_until, 'R')})")

        else:
            return
        if database.get('settings', entry.guild.id)[1] is not None:
            await self.bot.get_channel(database.get('settings', entry.guild.id)[1]).send(embed = embed)

    # VC参加/移動/退出
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.Member, after: discord.Member):
        if before.channel == after.channel:
            return
        if before.channel is None and after.channel is not None:
            embed = discord.Embed(title = t(member.guild.preferred_locale.value, "log.vc_join"),
                                  description = t(member.guild.preferred_locale.value, "log.vc_join_description", user=member.mention, channel=after.channel.mention),
                                  color = discord.Color.green())
        elif before.channel is not None and after.channel is None:
            embed = discord.Embed(title = t(member.guild.preferred_locale.value, "log.vc_leave"),
                                  description = t(member.guild.preferred_locale.value, "log.vc_leave_description", user=member.mention, channel=before.channel.mention),
                                  color = discord.Color.red())
        else:
            embed = discord.Embed(title = t(member.guild.preferred_locale.value, "log.vc_move"),
                                  description = t(member.guild.preferred_locale.value, "log.vc_move_description", user=member.mention, from_channel=before.channel.mention, to_channel=after.channel.mention),
                                  color = discord.Color.blurple())
        if database.get('settings', member.guild.id)[1] is not None:
            await self.bot.get_channel(database.get('settings', member.guild.id)[1]).send(embed = embed)
    
    
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(logger(bot))