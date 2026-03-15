import logging
import asyncio
from telethon import TelegramClient, events
from config import API_ID, API_HASH, CHANNELS

logger = logging.getLogger(__name__)

async def resolve_channels(client: TelegramClient, channels: list) -> list:
    """Resolves channel usernames/IDs into entity objects accepted by telethon."""
    resolved = []
    for channel in channels:
        try:
            if isinstance(channel, int):
                entity = await client.get_entity(channel)
            else:
                entity = await client.get_entity(channel)
            resolved.append(entity)
        except Exception as e:
            logger.error(f"Failed to resolve channel {channel}: {e}")
    return resolved

async def start_listener(callback_function):
    """
    Connects to Telegram, resolves the channels, and registers the callback
    for incoming messages.
    """
    if not API_ID or not API_HASH:
        logger.error("API_ID or API_HASH missing. Listener cannot start.")
        return

    client = TelegramClient('deal_sniper_session', API_ID, API_HASH)

    await client.start()
    logger.info("Telegram client started.")

    resolved_channels = await resolve_channels(client, CHANNELS)
    if not resolved_channels:
        logger.error("No valid channels to listen to.")
        return

    logger.info(f"Listening to channels: {[c.title for c in resolved_channels if hasattr(c, 'title')]}")

    @client.on(events.NewMessage(chats=resolved_channels))
    async def handler(event):
        try:
            text = event.raw_text or ""

            # ignore empty messages
            if not text:
                return

            # keep listener non-blocking
            result = callback_function(text)

            if asyncio.iscoroutine(result):
                asyncio.create_task(result)

        except Exception as e:
            logger.error(f"Error handling message: {e}")

    # Run the client until disconnected
    await client.run_until_disconnected()
