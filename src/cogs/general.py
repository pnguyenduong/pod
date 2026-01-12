import discord
from discord import app_commands
from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="ping", description="Checks the bot's latency.")
    async def ping(self, ctx: commands.Context):
        # Calculate latency in milliseconds
        latency_ms = round(self.bot.latency * 1000)
        await ctx.send(f"Pong! 🏓 ({latency_ms}ms)")

    @commands.hybrid_command(name="purge", description="Deletes a specified number of messages.")
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def purge(self, ctx: commands.Context, amount: int):
        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(f"Deleted {len(deleted)} messages.", delete_after=3, ephemeral=True)

    @purge.error
    async def purge_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to use this command.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))