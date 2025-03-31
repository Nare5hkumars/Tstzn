from asyncio import get_event_loop, sleep as asleep, gather
from traceback import format_exc
from aiohttp import web
from pyrogram import idle
from pyrogram import Client
from surftg import version, LOGGER
from surftg.config import Telegram
from surftg.server import web_server
from surftg.bot import StreamBot, UserBot
from surftg.bot.clients import initialize_clients

loop = get_event_loop()

app= Client("my_bot")

with app:
    chat_id="-1002231458694"
    from message in app.get_chat_history(chat_id=chat_id, limit=10):
        print(message.text)
async def start_services():
    """Start the bot and web server."""
    LOGGER.info(f'Initializing Surf-TG v-{version}')
    await asleep(1.2)

    await StreamBot.start()
    StreamBot.username = StreamBot.me.username
    LOGGER.info(f"✅ Bot Client: [@{StreamBot.username}]")

    if Telegram.SESSION_STRING:
        await UserBot.start()
        UserBot.username = UserBot.me.username or UserBot.me.first_name or str(UserBot.me.id)
        LOGGER.info(f"👤 User Client: {UserBot.username}")

    await asleep(1.2)
    LOGGER.info("🔄 Initializing Multi Clients...")
    await initialize_clients()

    await asleep(2)
    LOGGER.info('🌐 Initializing Surf Web Server...')
    server = web.AppRunner(await web_server())
    await server.setup()
    await web.TCPSite(server, '0.0.0.0', Telegram.PORT).start()

    LOGGER.info("🚀 Surf-TG Started Successfully!")
    await idle()


async def stop_clients():
    """Stop the bot clients when exiting."""
    await StreamBot.stop()

    if Telegram.SESSION_STRING and UserBot.is_connected:
        await UserBot.stop()


if __name__ == "__main__":
    try:
        loop.run_until_complete(start_services())
    except KeyboardInterrupt:
        LOGGER.info('🛑 Service Stopping...')
    except Exception:
        LOGGER.error(format_exc())
    finally:
        loop.run_until_complete(stop_clients())
        loop.stop()
