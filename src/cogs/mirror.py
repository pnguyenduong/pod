import asyncio
import logging
import discord
from discord.ext import commands

import config


class Mirror(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = logging.getLogger("bot.cogs.mirror")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        This event is triggered when a message is sent in a channel the bot can see.
        """
        # Ignore messages from the bot itself
        if message.author == self.bot.user:
            return

        # Iterate through all configured mirror mappings
        for mapping in getattr(config, "MIRROR_MAPPINGS", []):
            source_channel_id = mapping.get("SOURCE_CHANNEL_ID")

            # Check if the message matches the current mapping's source channel
            if message.channel.id == source_channel_id:
                target_channel_id = mapping.get("TARGET_CHANNEL_ID")
                if not target_channel_id:
                    continue  # Skip if no target is defined for this mapping

                target_channel = self.bot.get_channel(target_channel_id)
                if not target_channel:
                    continue  # Skip if the target channel is not found

                self.logger.info(f"Detected target match. MsgID: {message.id}. Initial Content: '{message.content}', Embeds: {len(message.embeds)}, Attachments: {len(message.attachments)}")

                # Wait a moment if the message appears empty (handles delayed edits/unfurls)
                if not message.content and not message.embeds and not message.attachments and not message.stickers:
                    self.logger.info("Message empty. Entering retry loop...")
                    # Retry loop: Some bots edit in the embed after a few seconds
                    for _ in range(5):  # Wait up to 10 seconds
                        await asyncio.sleep(2)
                        try:
                            message = await message.channel.fetch_message(message.id)
                            self.logger.info(f"Retry {_ + 1}: Content='{message.content}', Embeds={len(message.embeds)}")
                        except discord.NotFound:
                            self.logger.warning(f"Message {message.id} deleted before mirroring.")
                            return
                        
                        if message.content or message.embeds or message.attachments or message.stickers:
                            break

                # Replicate embeds
                new_embeds = [embed.copy() for embed in message.embeds]
                if new_embeds:
                    self.logger.info(f"Embed Data: {[e.to_dict() for e in new_embeds]}")

                # Replicate attachments
                files = [await attachment.to_file() for attachment in message.attachments]

                # Handle Stickers (fallback text if only stickers are present)
                content_to_send = message.content
                if not content_to_send and not new_embeds and not files and message.stickers:
                    sticker_names = ", ".join([s.name for s in message.stickers])
                    content_to_send = f"**[Sticker(s): {sticker_names}]**"

                # Check if there is any content to send to avoid HTTP 400 (Empty Message)
                if not content_to_send and not new_embeds and not files:
                    self.logger.warning(f"Skipping empty message {message.id} from {message.author} in {message.channel}. Type: {message.type}")
                    self.logger.warning(f"Debug: content='{content_to_send}', embeds={len(new_embeds)}, files={len(files)}")
                    return

                # Send the replicated message and stop checking other mappings
                try:
                    await target_channel.send(
                        content=content_to_send,
                        embeds=new_embeds,
                        files=files,
                    )
                    self.logger.info(f"Mirrored message {message.id} from {message.author} to {target_channel.name}.")
                except Exception as e:
                    self.logger.error(f"Failed to mirror message {message.id}: {e}")
                return


async def setup(bot: commands.Bot):
    await bot.add_cog(Mirror(bot))
