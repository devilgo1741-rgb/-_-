from pyrogram import filters, types
from anony import app, config


_cmd_filter = filters.create(
    lambda _, __, m: bool(
        m.text and m.text.startswith("/") and m.from_user
    )
)


@app.on_message(_cmd_filter, group=55)
async def _log_command(_, m: types.Message):
    try:
        if m.chat.id == app.logger:
            return
        if not app.logger:
            return

        cmd = m.text.split()[0].lstrip("/").split("@")[0]
        full_text = m.text[:200] if len(m.text) > 200 else m.text

        chat_info = (
            f"{m.chat.title} (<code>{m.chat.id}</code>)"
            if m.chat.title
            else f"<code>{m.chat.id}</code>"
        )

        text = (
            f"📋 <b>Command Log</b>\n\n"
            f"⚡ <b>Command:</b> <code>/{cmd}</code>\n"
            f"👤 <b>User:</b> {m.from_user.mention} (<code>{m.from_user.id}</code>)\n"
            f"💬 <b>Chat:</b> {chat_info}\n"
            f"📝 <b>Full:</b> <code>{full_text}</code>"
        )
        await app.send_message(chat_id=app.logger, text=text)
    except Exception:
        pass
