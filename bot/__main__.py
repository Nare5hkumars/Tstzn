import asyncio
from asyncio import get_event_loop, sleep as asleep
from traceback import format_exc
from aiohttp import web
from pyrogram import Client, idle
from bot import __version__, LOGGER
from bot.config import Telegram
from bot.server import web_server
from bot.telegram import StreamBot
from bot.telegram.clients import initialize_clients

# Initialize UserBot client
app = Client("userbot", Telegram.API_ID, Telegram.API_HASH, session_string=Telegram.SESSION_STRING)

async def get_chat_id_and_messages():
    """Fetch chat ID and last 10 messages from a private channel using UserBot."""
    chat_id = Telegram.PRIVATE_CHANNEL_ID  # Get from config.py

    async with app:  # ✅ Ensure app is started
        try:
            chat = await app.get_chat(chat_id)  # ✅ Use `app`, not `UserBot`
            LOGGER.info(f"✅ Private Channel ID: {chat.id}")

            LOGGER.info(f"📥 Fetching last 10 messages from {chat_id}...")
            async for message in app.get_chat_history(chat_id, limit=10):
                LOGGER.info(f"{message.date} - {message.text}")

        except Exception as e:
            LOGGER.error(f"❌ Error fetching messages: {e}")

async def start_services():
    """Initialize the bot and fetch chat details."""
    LOGGER.info(f'Initializing Surf-TG v-{__version__}')
    await asleep(1.2)
    
    await StreamBot.start()
    StreamBot.username = StreamBot.me.username
    LOGGER.info(f"🤖 Bot Client: [@{StreamBot.username}]")

    if Telegram.SESSION_STRING:
        await app.start()
        user = await app.get_me()
        LOGGER.info(f"👤 User Client: {user.username or user.first_name or user.id}")
    
    await asleep(1.2)
    LOGGER.info("🔄 Initializing Multi Clients")
    await initialize_clients()

    # ✅ Fetch Chat ID and Messages After Bot Starts
    await get_chat_id_and_messages()

    await asleep(2)
    LOGGER.info('🌐 Initializing Web Server...')
    server = web.AppRunner(await web_server())
    await server.setup()
    await web.TCPSite(server, '0.0.0.0', Telegram.PORT).start()

    LOGGER.info("🎯 Surf-TG Started Successfully!")
    await idle()

async def stop_clients():
    """Stop the bot clients when exiting."""
    await StreamBot.stop()
    if Telegram.SESSION_STRING:
        await app.stop()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(start_services())
    except KeyboardInterrupt:
        LOGGER.info('🛑 Service Stopping...')
    except Exception:
        LOGGER.error(format_exc())
    finally:
        loop.run_until_complete(stop_clients())
        loop.stop()
