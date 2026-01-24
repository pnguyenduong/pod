import discord
import logging
from discord.ext import commands
import config

class Welcome(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = logging.getLogger("bot.cogs.welcome")

    @commands.Cog.listener()
    async def on_ready(self):

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.bot:
            return

        # Send to the specific welcome channel
        channel = member.guild.get_channel(config.WELCOME_CHANNEL_ID)

        # Fallback: Try fetching from API if not in cache
        if channel is None:
            try:
                channel = await member.guild.fetch_channel(config.WELCOME_CHANNEL_ID)
            except Exception as e:
                self.logger.warning(f"Failed to fetch welcome channel (ID: {config.WELCOME_CHANNEL_ID}): {e}")

        if channel is not None:
            try:
                await channel.send(f"Welcome to the server, {member.mention}! 🎉")
                self.logger.info(f"Sent welcome message to {channel.name}")
            except discord.Forbidden:
                self.logger.error(f"Missing permissions to send welcome message in {channel.name} ({channel.id})")
            except Exception as e:
                self.logger.error(f"Failed to send welcome message: {e}")
        else:
            self.logger.warning(f"Welcome channel ID {config.WELCOME_CHANNEL_ID} not found in guild {member.guild.name}")

    @commands.hybrid_command(name="testwelcome", description="Test the welcome message configuration.")
    @commands.has_permissions(administrator=True)
    async def test_welcome(self, ctx: commands.Context):
        """Debug command to verify welcome channel settings."""
        # 1. Verify Member Cache (Intents Check)
        # If get_member returns None, the bot is 'blind' to members due to missing Intents or caching issues.
        if not ctx.guild.get_member(ctx.author.id):
            await ctx.send("⚠️ **CRITICAL WARNING**: I cannot find you in my member cache. This means **Server Members Intent** is likely disabled or not working. The `on_member_join` event will NOT fire.")

        channel_id = config.WELCOME_CHANNEL_ID
        channel = ctx.guild.get_channel(channel_id)

        if not channel:
            try:
                channel = await ctx.guild.fetch_channel(channel_id)
            except discord.NotFound:
                await ctx.send(f"❌ **Error**: Channel ID `{channel_id}` not found. Check `src/config.py`.")
                return
            except discord.Forbidden:
                await ctx.send(f"❌ **Error**: Bot cannot view channel `{channel_id}` (Missing Permissions).")
                return

        try:
            await channel.send(f"Welcome to the server, {ctx.author.mention}! 🎉 (Test Message)")
            await ctx.send(f"✅ **Success**: Test message sent to {channel.mention}.")
        except discord.Forbidden:
            await ctx.send(f"❌ **Error**: Bot cannot send messages in {channel.mention}.")
        except Exception as e:
            await ctx.send(f"❌ **Error**: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Welcome(bot))