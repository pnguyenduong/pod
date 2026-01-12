import discord
from discord.ext import commands
import config

class Welcome(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        # Send to the specific welcome channel
        channel = member.guild.get_channel(config.WELCOME_CHANNEL_ID)
        if channel is not None:
            await channel.send(f"Welcome to the server, {member.mention}! 🎉")

async def setup(bot: commands.Bot):
    await bot.add_cog(Welcome(bot))