import asyncio
from pyrogram import filters, StopPropagation, types
from anony import app, config

app.maintenance_mode = False

MAINTENANCE_ON = (
    "🛠 <b>Maintenance Mode ON</b>\n\n"
    "Bot abhi maintenance pe hai.\n"
    "Sabhi commands temporarily band hain.\n\n"
    "Wapas activate karne ke liye:\n"
    "<code>/maintenance off</code>"
)

MAINTENANCE_OFF = (
    "✅ <b>Maintenance Mode OFF</b>\n\n"
    "Bot ab poori tarah active hai!\n"
    "Sab commands kaam kar rahe hain."
)

MAINTENANCE_MSG = (
    "🛠 <b>Bot Under Maintenance</b>\n\n"
    "Hum kuch improvements kar rahe hain.\n"
    "Thodi der baad try karein. 🙏"
)

@app.on_message(filters.all, group=-998)
async def _maintenance_blocker(_, m: types.Message):
    if not app.maintenance_mode:
        return
    if m.from_user and m.from_user.id == config.OWNER_ID:
        return
    if m.text and m.text.strip().startswith("/"):
        try:
            await m.reply_text(MAINTENANCE_MSG)
        except Exception:
            pass
    raise StopPropagation


@app.on_message(filters.command(["maintenance"]) & filters.user(config.OWNER_ID))
async def _maintenance_cmd(_, m: types.Message):
    args = m.command[1].lower() if len(m.command) > 1 else ""

    if args == "off":
        if not app.maintenance_mode:
            return await m.reply_text("✅ Bot pehle se hi active hai.")
        app.maintenance_mode = False
        return await m.reply_text(MAINTENANCE_OFF)

    if app.maintenance_mode:
        return await m.reply_text("🛠 Bot pehle se hi maintenance mode mein hai.")

    app.maintenance_mode = True
    await m.reply_text(MAINTENANCE_ON)
