import os
import sys
import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest
from discord.ext import commands

# Add project root to path to allow importing from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.cogs.logger import Logger
from src import config

# Pytest-asyncio mark
pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_bot():
    """Fixture for a mocked bot."""
    bot = MagicMock(spec=commands.Bot)
    bot.get_channel = MagicMock()
    return bot

@pytest.fixture
def logger_cog(mock_bot):
    """Fixture for the Logger cog."""
    return Logger(mock_bot)

@patch('src.cogs.logger.discord.utils.utcnow')
async def test_on_message_delete_sends_log(mock_utcnow, logger_cog, mock_bot):
    """
    Test that on_message_delete sends a correctly formatted log.
    """
    # --- Arrange ---
    mock_utcnow.return_value = datetime.datetime(2026, 1, 19, 12, 0, 0, tzinfo=datetime.timezone.utc)
    mock_log_channel = AsyncMock(spec=discord.TextChannel)
    mock_bot.get_channel.return_value = mock_log_channel

    mock_author = MagicMock(spec=discord.Member)
    mock_author.bot = False
    mock_author.name = "TestUser"
    mock_author.id = 12345
    mock_author.__str__.return_value = "TestUser"
    mock_author.display_avatar.url = "http://example.com/avatar.png"

    mock_channel = MagicMock(spec=discord.TextChannel)
    mock_channel.mention = "#test-channel"

    mock_message = MagicMock(spec=discord.Message)
    mock_message.author = mock_author
    mock_message.channel = mock_channel
    mock_message.content = "This was the message content."
    mock_message.attachments = []
    mock_message.id = 67890
    mock_message.guild.id = 54321

    # --- Act ---
    await logger_cog.on_message_delete(mock_message)

    # --- Assert ---
    mock_bot.get_channel.assert_called_once_with(config.LOG_CHANNEL_MESSAGES)
    mock_log_channel.send.assert_called_once()
    
    _args, kwargs = mock_log_channel.send.call_args
    sent_embed = kwargs['embed']

    assert sent_embed.title == "🗑️ Message Deleted"
    assert sent_embed.color == discord.Color.red()
    assert sent_embed.author.name == "TestUser (12345)"
    assert sent_embed.author.icon_url == "http://example.com/avatar.png"
    assert "#test-channel" in sent_embed.description
    assert "This was the message content." in sent_embed.description
    assert sent_embed.footer.text == "Message ID: 67890"

async def test_on_guild_channel_update_sends_log(logger_cog, mock_bot):
    """
    Test that on_guild_channel_update sends a log on name change.
    """
    # --- Arrange ---
    mock_log_channel = AsyncMock(spec=discord.TextChannel)
    mock_bot.get_channel.return_value = mock_log_channel

    mock_before_channel = MagicMock(spec=discord.TextChannel)
    mock_before_channel.name = "old-name"
    
    mock_after_channel = MagicMock(spec=discord.TextChannel)
    mock_after_channel.name = "new-name"
    mock_after_channel.mention = "#new-name"
    mock_after_channel.id = 98765

    # --- Act ---
    await logger_cog.on_guild_channel_update(mock_before_channel, mock_after_channel)

    # --- Assert ---
    mock_bot.get_channel.assert_called_once_with(config.LOG_CHANNEL_SERVER)
    mock_log_channel.send.assert_called_once()

    _args, kwargs = mock_log_channel.send.call_args
    sent_embed = kwargs['embed']

    assert sent_embed.title == "Channel Updated"
    assert "Name changed: `#old-name` → `#new-name`" in sent_embed.description
    assert f"ID: {mock_after_channel.id}" in sent_embed.footer.text