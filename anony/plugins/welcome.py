from pyrogram import enums, filters, types
from anony import app


@app.on_message(filters.new_chat_members, group=9)
async def _welcome_member(_, m: types.Message):
    try:
        for member in m.new_chat_members:
            if member.is_bot:
                continue
            if member.id == app.id:
                continue

            mention = member.mention
            chat_title = m.chat.title or "this group"

            await m.reply_text(
                f"🎉 <b>Welcome to {chat_title}!</b>\n\n"
                f"👋 Aagaye {mention} !\n\n"
                f"╔══════════════════╗\n"
                f"║   🎵  Music Bot  🎵   ║\n"
                f"╚══════════════════╝\n\n"
                f"🎶 Music sunne ke liye <code>/play song name</code> use karo\n"
                f"📋 Sab commands ke liye <code>/cmds</code> likhao\n\n"
                f"<i>Enjoy your time here! 😊</i>"
            )
    except Exception:
        pass
