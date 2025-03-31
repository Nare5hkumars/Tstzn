from asyncio import get_event_loop, sleep as asleep, gather
from traceback import format_exc
from aiohttp import web
from pyrogram import idle
from bot import __version__, LOGGER
from bot.config import Telegram
from bot.server import web_server
from bot.telegram import StreamBot, UserBot
from bot.telegram.clients import initialize_clients

loop = get_event_loop()

async def get_chat_id_and_messages():
    """Fetch chat ID and the last 10 messages from a group or channel."""
    chat_username = "@t.me/+WS7_EUx46RRkMTll"  # Replace with your group/channel username
    try:
        chat = await StreamBot.get_chat(chat_username)
        chat_id = chat.id
        LOGGER.info(f"✅ Chat ID for {chat_username}: {chat_id}")

        LOGGER.info(f"📥 Fetching last 10 messages from {chat_id}...")
        async for message in StreamBot.get_chat_history(chat_id, limit=10):
            LOGGER.info(f"{message.date} - {message.text}")

    except Exception as e:
        LOGGER.error(f"❌ Error fetching chat info: {e}")

async def start_services():
    """Initialize the bot and fetch chat details."""
    LOGGER.info(f'Initializing Surf-TG v-{__version__}')
    await asleep(1.2)
    
    await StreamBot.start()
    StreamBot.username = StreamBot.me.username
    LOGGER.info(f"🤖 Bot Client: [@{StreamBot.username}]")

    if len(Telegram.SESSION_STRING) != 0:
        await UserBot.start()
        UserBot.username = UserBot.me.username or UserBot.me.first_name or UserBot.me.id
        LOGGER.info(f"👤 User Client: {UserBot.username}")
    
    await asleep(1.2)
    LOGGER.info("🔄 Initializing Multi Clients")
    await initialize_clients()

    # ✅ Fetch Chat ID and Messages After Bot Starts
    await get_chat_id_and_messages()

    await asleep(2)
    LOGGER.info('🌐 Initializing Web Server...')
    server = web.AppRunner(await web_server())
    LOGGER.info("🔧 Server CleanUp!")
    await server.cleanup()
    
    await asleep(2)
    LOGGER.info("🚀 Server Setup Started!")
    
    await server.setup()
    await web.TCPSite(server, '0.0.0.0', Telegram.PORT).start()

    LOGGER.info("🎯 Surf-TG Started Successfully!")
    await idle()

async def stop_clients():
    """Stop the bot clients when exiting."""
    await StreamBot.stop()
    if len(Telegram.SESSION_STRING) != 0:
        await UserBot.stop()

if __name__ == '__main__':
    try:
        loop.run_until_complete(start_services())
    except KeyboardInterrupt:
        LOGGER.info('🛑 Service Stopping...')
    except Exception:
        LOGGER.error(format_exc())
    finally:
        loop.run_until_complete(stop_clients())
        loop.stop()
