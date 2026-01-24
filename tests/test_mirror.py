import os
import sys
from unittest.mock import AsyncMock, MagicMock

import discord
import pytest
from discord.ext import commands

# Add project root to path to allow importing from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.cogs.mirror import Mirror
from src import config

# Pytest-asyncio mark
pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_bot():
    """Fixture for a mocked bot."""
    bot = MagicMock(spec=commands.Bot)
    bot.user = MagicMock(spec=discord.ClientUser)
    bot.user.id = 9876543210
    bot.get_channel = MagicMock()
    return bot

@pytest.fixture
def mirror_cog(mock_bot):
    """Fixture for the Mirror cog."""
    return Mirror(mock_bot)

async def test_on_message_no_mirror_if_from_bot_itself(mirror_cog, mock_bot):
    """Test that the bot doesn't mirror its own messages."""
    # --- Arrange ---
    message = MagicMock(spec=discord.Message)
    message.author = mock_bot.user
    
    # --- Act ---
    await mirror_cog.on_message(message)

    # --- Assert ---
    mock_bot.get_channel.assert_not_called()


async def test_on_message_no_mirror_if_not_in_any_source_channel(mirror_cog, mock_bot):
    """Test that the bot doesn't mirror messages from unconfigured channels."""
    # --- Arrange ---
    setattr(config, "MIRROR_MAPPINGS", [{
        "SOURCE_CHANNEL_ID": 111,
        "TARGET_CHANNEL_ID": 222,
        "BOT_TO_MIRROR_ID": 12345
    }])
    message = MagicMock(spec=discord.Message)
    message.channel = MagicMock(spec=discord.TextChannel)
    message.channel.id = 999  # Different channel
    message.author = MagicMock(spec=discord.Member)
    message.author.id = 12345

    # --- Act ---
    await mirror_cog.on_message(message)

    # --- Assert ---
    mock_bot.get_channel.assert_not_called()

async def test_on_message_no_mirror_if_not_correct_bot_id(mirror_cog, mock_bot):
    """Test that the bot doesn't mirror messages from unconfigured authors."""
    # --- Arrange ---
    setattr(config, "MIRROR_MAPPINGS", [{
        "SOURCE_CHANNEL_ID": 111,
        "TARGET_CHANNEL_ID": 222,
        "BOT_TO_MIRROR_ID": 12345
    }])
    message = MagicMock(spec=discord.Message)
    message.channel = MagicMock(spec=discord.TextChannel)
    message.channel.id = 111
    message.author = MagicMock(spec=discord.Member)
    message.author.id = 54321 # Different author

    # --- Act ---
    await mirror_cog.on_message(message)
    # --- Assert ---
    mock_bot.get_channel.assert_not_called()

async def test_on_message_mirrors_correctly_for_first_mapping(mirror_cog, mock_bot):
    """Test that the bot mirrors a message matching the first of two mappings."""
    # --- Arrange ---
    MAPPINGS = [
        { "SOURCE_CHANNEL_ID": 111, "TARGET_CHANNEL_ID": 222, "BOT_TO_MIRROR_ID": 123 },
        { "SOURCE_CHANNEL_ID": 333, "TARGET_CHANNEL_ID": 444, "BOT_TO_MIRROR_ID": 456 },
    ]
    setattr(config, "MIRROR_MAPPINGS", MAPPINGS)

    mock_target_channel = AsyncMock(spec=discord.TextChannel)
    mock_bot.get_channel.return_value = mock_target_channel

    message = MagicMock(spec=discord.Message)
    message.channel = MagicMock(spec=discord.TextChannel)
    message.channel.id = 111  # Matches first mapping
    message.author = MagicMock(spec=discord.Member)
    message.author.id = 123  # Matches first mapping
    message.content = "Hello World"
    
    mock_embed = MagicMock(spec=discord.Embed)
    mock_embed.copy.return_value = "copied_embed"
    message.embeds = [mock_embed]

    mock_attachment = MagicMock(spec=discord.Attachment)
    mock_attachment.to_file = AsyncMock(return_value="file_content")
    message.attachments = [mock_attachment]

    # --- Act ---
    await mirror_cog.on_message(message)

    # --- Assert ---
    mock_bot.get_channel.assert_called_once_with(222)  # Correct target
    mock_target_channel.send.assert_called_once_with(
        content="Hello World",
        embeds=["copied_embed"],
        files=["file_content"],
    )

async def test_on_message_mirrors_correctly_for_second_mapping(mirror_cog, mock_bot):
    """Test that the bot mirrors a message matching the second of two mappings."""
    # --- Arrange ---
    MAPPINGS = [
        { "SOURCE_CHANNEL_ID": 111, "TARGET_CHANNEL_ID": 222, "BOT_TO_MIRROR_ID": 123 },
        { "SOURCE_CHANNEL_ID": 333, "TARGET_CHANNEL_ID": 444, "BOT_TO_MIRROR_ID": 456 },
    ]
    setattr(config, "MIRROR_MAPPINGS", MAPPINGS)

    mock_target_channel = AsyncMock(spec=discord.TextChannel)
    mock_bot.get_channel.return_value = mock_target_channel

    message = MagicMock(spec=discord.Message)
    message.channel = MagicMock(spec=discord.TextChannel)
    message.channel.id = 333 # Matches second mapping
    message.author = MagicMock(spec=discord.Member)
    message.author.id = 456 # Matches second mapping
    message.content = "Second Test"
    message.embeds = []
    message.attachments = []

    # --- Act ---
    await mirror_cog.on_message(message)

    # --- Assert ---
    mock_bot.get_channel.assert_called_once_with(444)  # Correct target
    mock_target_channel.send.assert_called_once_with(
        content="Second Test",
        embeds=[],
        files=[],
    )
