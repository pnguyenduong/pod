import discord
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="help", description="Displays the list of available commands.")
    async def help(self, ctx: commands.Context, command_name: str = None):
        """
        Displays the list of available commands or details for a specific command.
        """
        if command_name:
            # Help for a specific command
            cmd = self.bot.get_command(command_name)
            if not cmd or cmd.hidden:
                await ctx.send(f"❌ Command `{command_name}` not found.", ephemeral=True)
                return

            embed = discord.Embed(title=f"Command: {cmd.name}", description=cmd.description or "No description provided.", color=discord.Color.blue())
            if cmd.aliases:
                embed.add_field(name="Aliases", value=", ".join(cmd.aliases), inline=False)
            
            # Usage syntax (basic)
            params = []
            for key, value in cmd.clean_params.items():
                params.append(f"<{key}>" if value.default is value.empty else f"[{key}]")
            usage = f"/{cmd.name} " + " ".join(params)
            embed.add_field(name="Usage", value=f"`{usage}`", inline=False)

            await ctx.send(embed=embed)
        else:
            # General Help
            embed = discord.Embed(title="📚 Bot Commands", description="Here are the available commands:", color=discord.Color.blue())
            
            for cog_name, cog in self.bot.cogs.items():
                commands_list = []
                for cmd in cog.get_commands():
                    if not cmd.hidden:
                        commands_list.append(f"`{cmd.name}`")
                
                if commands_list:
                    embed.add_field(name=cog_name, value=", ".join(commands_list), inline=False)
            
            # Uncategorized
            uncogged = [f"`{c.name}`" for c in self.bot.commands if c.cog is None and not c.hidden]
            if uncogged:
                embed.add_field(name="Uncategorized", value=", ".join(uncogged), inline=False)

            embed.set_footer(text="Type /help <command> for more info.")
            await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))