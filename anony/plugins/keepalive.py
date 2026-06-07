import asyncio
import time
import psutil
from aiohttp import web

from anony import app, anon, boot, db, logger, tasks


_status_msg_id = None


async def send_status():
    global _status_msg_id
    await asyncio.sleep(20)

    while True:
        try:
            secs = int(time.time() - boot)
            h, rem = divmod(secs, 3600)
            m, s = divmod(rem, 60)
            uptime = f"{h}h {m}m {s}s"

            active = len(db.active_calls)
            cpu = psutil.cpu_percent(interval=0)
            ram = psutil.virtual_memory().percent

            text = (
                f"💓 <b>Bot Status Update</b>\n\n"
                f"🤖 <b>Bot:</b> @{app.username}\n"
                f"⏰ <b>Uptime:</b> <code>{uptime}</code>\n"
                f"🎵 <b>Active VCs:</b> <code>{active}</code>\n"
                f"💾 <b>RAM:</b> <code>{ram}%</code>\n"
                f"⚡ <b>CPU:</b> <code>{cpu}%</code>\n"
                f"🔄 <b>Status:</b> <code>Online ✅</code>"
            )

            if _status_msg_id:
                try:
                    await app.edit_message_text(
                        chat_id=app.logger,
                        message_id=_status_msg_id,
                        text=text,
                    )
                except Exception:
                    msg = await app.send_message(chat_id=app.logger, text=text)
                    _status_msg_id = msg.id
            else:
                msg = await app.send_message(chat_id=app.logger, text=text)
                _status_msg_id = msg.id

        except Exception as e:
            logger.warning(f"Keepalive error: {e}")

        await asyncio.sleep(300)


async def health_handler(request):
    return web.Response(text="OK")


async def run_health_server():
    runner_app = web.Application()
    runner_app.router.add_get("/", health_handler)
    runner_app.router.add_get("/health", health_handler)
    runner = web.AppRunner(runner_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    try:
        await site.start()
        logger.info("Health server started on port 8080")
    except Exception as e:
        logger.warning(f"Health server failed: {e}")
    while True:
        await asyncio.sleep(3600)


tasks.append(asyncio.create_task(send_status()))
tasks.append(asyncio.create_task(run_health_server()))
