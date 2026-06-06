from pyrogram import filters, StopPropagation, types

from anony import anon, app, config, db


app.sleep_mode = False

SLEEP_ON_TEXT = (
    "😴 <b>Bot ab so gaya hai!</b>\n\n"
    "Tamam active calls band kar di gayi hain.\n"
    "Dobara activate karne ke liye <code>/sleep off</code> bhejo."
)

SLEEP_OFF_TEXT = (
    "✅ <b>Bot phir se active ho gaya!</b>\n\n"
    "Ab sab commands kaam karenge."
)

ALREADY_SLEEPING = "😴 Bot pehle se hi so raha hai. <code>/sleep off</code> se jagao."
ALREADY_AWAKE = "✅ Bot pehle se hi active hai."


@app.on_message(filters.all, group=-999)
async def _sleep_blocker(_, m: types.Message):
    if not app.sleep_mode:
        return

    if m.from_user and m.from_user.id == config.OWNER_ID:
        if m.text and m.text.strip().lower() in ("/sleep off", f"/sleep off@{app.username}"):
            return

    raise StopPropagation


@app.on_message(
    filters.command(["sleep"]) & filters.user(config.OWNER_ID)
)
async def _sleep_cmd(_, m: types.Message):
    args = m.command[1].lower() if len(m.command) > 1 else ""

    if args == "off":
        if not app.sleep_mode:
            return await m.reply_text(ALREADY_AWAKE)
        app.sleep_mode = False
        return await m.reply_text(SLEEP_OFF_TEXT)

    if app.sleep_mode:
        return await m.reply_text(ALREADY_SLEEPING)

    app.sleep_mode = True

    active = list(db.active_calls)
    for chat_id in active:
        try:
            await anon.stop(chat_id)
        except Exception:
            pass

    stopped = len(active)
    text = SLEEP_ON_TEXT
    if stopped:
        text += f"\n\n🔇 <b>{stopped}</b> active call(s) band ki gayi."

    await m.reply_text(text)
