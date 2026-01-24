import discord
from discord.ext import commands
import aiohttp
import io
import logging

import config

class Logger(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = logging.getLogger("bot.cogs.logger")
        
        # --- CONFIGURATION ---
        self.log_channel_messages = config.LOG_CHANNEL_MESSAGES
        self.log_channel_members = config.LOG_CHANNEL_MEMBERS
        self.log_channel_moderation = config.LOG_CHANNEL_MODERATION
        self.log_channel_server = config.LOG_CHANNEL_SERVER
        self.log_channel_voice = config.LOG_CHANNEL_VOICE

    async def _send_log(self, channel_id: int, embed: discord.Embed, files: list = None):
        """Helper to send log to a specific channel if ID is set."""
        if not channel_id:
            return

        try:
            cid = int(channel_id)
            if cid == 0:
                return
        except (ValueError, TypeError):
            self.logger.error(f"Invalid channel ID provided: '{channel_id}'. Must be an integer.")
            return
            
        channel = self.bot.get_channel(cid)
        if not channel:
            self.logger.warning(f"Log channel with ID {cid} not found.")
            return

        try:
            await channel.send(embed=embed, files=files or [])
        except discord.errors.Forbidden:
            self.logger.warning(f"Missing permissions to send message in channel {channel.name} ({channel.id}).")
        except Exception as e:
            self.logger.error(f"Could not send log to channel {channel.id}: {e}")

    # --- 1. MESSAGES & IMAGES ---
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot: return
        
        embed = discord.Embed(title="🗑️ Message Deleted", color=discord.Color.red(), timestamp=discord.utils.utcnow())
        embed.set_author(name=f"{message.author} ({message.author.id})", icon_url=message.author.display_avatar.url)
        embed.description = f"**Channel:** {message.channel.mention}\n**Content:** {message.content or '*[No text]*'}"
        embed.set_footer(text=f"Message ID: {message.id}")

        files = []
        # Attempt to rescue images
        if message.attachments:
            embed.add_field(name="Attachments", value=f"{len(message.attachments)} file(s) found.", inline=False)
            async with aiohttp.ClientSession() as session:
                for attachment in message.attachments:
                    if attachment.content_type and attachment.content_type.startswith('image/'):
                        try:
                            async with session.get(attachment.url) as resp:
                                if resp.status == 200:
                                    data = io.BytesIO(await resp.read())
                                    files.append(discord.File(data, filename=attachment.filename))
                        except Exception:
                            pass # Image might be gone already

        await self._send_log(self.log_channel_messages, embed, files=files)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot or before.content == after.content: return

        embed = discord.Embed(title="✏️ Message Edited", color=discord.Color.orange(), timestamp=discord.utils.utcnow())
        embed.set_author(name=f"{before.author} ({before.author.id})", icon_url=before.author.display_avatar.url)
        embed.description = f"**Channel:** {before.channel.mention} [Jump to Message]({before.jump_url})"
        embed.add_field(name="Before", value=before.content or "*[No text]*", inline=False)
        embed.add_field(name="After", value=after.content or "*[No text]*", inline=False)
        
        await self._send_log(self.log_channel_messages, embed)

    # --- 2. MEMBERS ---
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        embed = discord.Embed(title="📥 Member Joined", color=discord.Color.green(), timestamp=discord.utils.utcnow())
        embed.set_author(name=f"{member} ({member.id})", icon_url=member.display_avatar.url)
        embed.add_field(name="Account Created", value=discord.utils.format_dt(member.created_at, style='R'))
        await self._send_log(self.log_channel_members, embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        # Check Audit Logs to see if this was a Kick
        is_kick = False
        executor = None
        reason = None

        if member.guild.me.guild_permissions.view_audit_log:
            async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
                if entry.target.id == member.id:
                    if (discord.utils.utcnow() - entry.created_at).total_seconds() < 5:
                        is_kick = True
                        executor = entry.user
                        reason = entry.reason
                        break

        if is_kick:
            embed = discord.Embed(title="🥾 Member Kicked", color=discord.Color.orange(), timestamp=discord.utils.utcnow())
            embed.set_author(name=f"{member} ({member.id})", icon_url=member.display_avatar.url)
            embed.add_field(name="Kicked By", value=executor.mention, inline=True)
            embed.add_field(name="Reason", value=reason or "No reason provided", inline=False)
            await self._send_log(self.log_channel_moderation, embed)
        else:
            embed = discord.Embed(title="📤 Member Left", color=discord.Color.dark_grey(), timestamp=discord.utils.utcnow())
            embed.set_author(name=f"{member} ({member.id})", icon_url=member.display_avatar.url)
            await self._send_log(self.log_channel_members, embed)

    # --- 3. MODERATION (Bans) ---
    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        embed = discord.Embed(title="🔨 Member Banned", color=discord.Color.dark_red(), timestamp=discord.utils.utcnow())
        embed.set_author(name=f"{user} ({user.id})", icon_url=user.display_avatar.url)
        await self._send_log(self.log_channel_moderation, embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        embed = discord.Embed(title="🔓 Member Unbanned", color=discord.Color.green(), timestamp=discord.utils.utcnow())
        embed.set_author(name=f"{user} ({user.id})", icon_url=user.display_avatar.url)
        await self._send_log(self.log_channel_moderation, embed)

    # --- 4. SERVER (Roles, Channels, Emojis) ---
    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        embed = discord.Embed(title="🛡️ Role Created", description=role.name, color=discord.Color.blue(), timestamp=discord.utils.utcnow())
        await self._send_log(self.log_channel_server, embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        embed = discord.Embed(title="📺 Channel Created", description=channel.name, color=discord.Color.blue(), timestamp=discord.utils.utcnow())
        await self._send_log(self.log_channel_server, embed)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
        """Logs channel updates, specifically name changes."""
        if before.name == after.name:
            return

        description = (
            f"🪭\u2060│ {after.mention}\n"
            f"Name changed: `#{before.name}` → `#{after.name}`"
        )
        
        embed = discord.Embed(
            title="Channel Updated",
            description=description,
            color=discord.Color.blue(),
        )
        
        embed.set_footer(text=f"ID: {after.id} • {discord.utils.format_dt(discord.utils.utcnow(), style='R')}")

        await self._send_log(self.log_channel_server, embed)

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild, before, after):
        embed = discord.Embed(title="😀 Emojis Updated", description=f"Total Emojis: {len(after)}", color=discord.Color.blue(), timestamp=discord.utils.utcnow())
        await self._send_log(self.log_channel_server, embed)

    # --- 5. VOICE ---
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel == after.channel: return # Ignore mute/deafen toggles

        embed = discord.Embed(timestamp=discord.utils.utcnow(), color=discord.Color.purple())
        embed.set_author(name=f"{member} ({member.id})", icon_url=member.display_avatar.url)

        if before.channel is None:
            embed.title = "🎙️ Joined Voice"
            embed.description = f"Joined **{after.channel.name}**"
        elif after.channel is None:
            embed.title = "🔇 Left Voice"
            embed.description = f"Left **{before.channel.name}**"
        else:
            embed.title = "🔄 Moved Voice"
            embed.description = f"Moved from **{before.channel.name}** to **{after.channel.name}**"

        await self._send_log(self.log_channel_voice, embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Logger(bot))