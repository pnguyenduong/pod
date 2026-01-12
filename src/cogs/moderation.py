import discord
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="kick", description="Kicks a member from the server.")
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason: str = "No reason provided"):
        # Role hierarchy check
        if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            await ctx.send("You cannot kick this member due to role hierarchy.", ephemeral=True)
            return
        
        await member.kick(reason=reason)
        
        embed = discord.Embed(title="🥾 Member Kicked", color=discord.Color.orange())
        embed.add_field(name="User", value=f"{member} ({member.id})", inline=True)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="ban", description="Bans a user from the server.")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: str = "No reason provided"):
        # Role hierarchy check
        if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            await ctx.send("You cannot ban this member due to role hierarchy.", ephemeral=True)
            return

        await member.ban(reason=reason)

        embed = discord.Embed(title="🔨 Member Banned", color=discord.Color.red())
        embed.add_field(name="User", value=f"{member} ({member.id})", inline=True)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="unban", description="Unbans a user from the server.")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx: commands.Context, user: discord.User, *, reason: str = "No reason provided"):
        try:
            await ctx.guild.unban(user, reason=reason)
        except discord.NotFound:
            await ctx.send("This user is not banned.", ephemeral=True)
            return
        except Exception as e:
            await ctx.send(f"Failed to unban user: {e}", ephemeral=True)
            return

        embed = discord.Embed(title="🔓 Member Unbanned", color=discord.Color.green())
        embed.add_field(name="User", value=f"{user} ({user.id})", inline=True)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)

        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
