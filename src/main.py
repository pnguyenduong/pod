import asyncio
import logging
import os
import sys
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

from database import DatabaseManager

# 1. Load Environment Variables
load_dotenv()

# 2. Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("bot")

class Bot(commands.Bot):
    def __init__(self):
        # Define Intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None,  # Custom help command can be added later
        )
        self.db = DatabaseManager(os.getenv("DB_FILENAME", "database.db"))

    async def setup_hook(self):
        """
        Asynchronous setup code (loading extensions, syncing commands).
        """
        await self.db.connect()

        # Load Cogs
        cogs_dir = Path(__file__).parent / "cogs"
        if cogs_dir.exists():
            for file in cogs_dir.glob("*.py"):
                if file.name == "__init__.py":
                    continue
                
                # Assuming running from src/ or src is in path
                extension_name = f"cogs.{file.stem}"
                try:
                    await self.load_extension(extension_name)
                    logger.info(f"Loaded extension: {extension_name}")
                except Exception as e:
                    logger.error(f"Failed to load extension {extension_name}: {e}")

        # Sync Slash Commands
        # Note: Global sync can take up to an hour. For dev, sync to guild is faster.
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s) globally.")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")

    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        # If the command has a local error handler, ignore global handling
        if hasattr(ctx.command, 'on_error'):
            return

        # Get original error if available
        error = getattr(error, 'original', error)

        if isinstance(error, commands.CommandNotFound):
            return  # Ignore

        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to use this command.", delete_after=5)
            return

        logger.error(f"Error in command {ctx.command}: {error}", exc_info=True)

    async def close(self):
        await self.db.close()
        await super().close()

    async def on_ready(self):
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info("-------------------------------------------")

async def main():
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.critical("DISCORD_TOKEN not found in .env file.")
        return

    bot = Bot()
    async with bot:
        await bot.start(token)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass