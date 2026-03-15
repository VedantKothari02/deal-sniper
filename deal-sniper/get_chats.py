from telethon import TelegramClient
from config import API_ID, API_HASH

async def main():
    async with TelegramClient("deal_sniper_session", API_ID, API_HASH) as client:
        dialogs = await client.get_dialogs()

        for d in dialogs:
            print(d.name, d.id)

import asyncio
asyncio.run(main())