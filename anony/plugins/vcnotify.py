from pyrogram import filters, types
from anony import app


@app.on_message(filters.video_chat_started, group=18)
async def _vc_started(_, m: types.Message):
    try:
        starter = m.from_user.mention if m.from_user else "Someone"
        await m.reply_text(
            f"🎙️ <b>Voice Chat Started!</b>\n\n"
            f"╔══════════════════╗\n"
            f"║    🔴  LIVE  🔴    ║\n"
            f"╚══════════════════╝\n\n"
            f"👤 <b>Started by:</b> {starter}\n"
            f"💬 <b>Chat:</b> {m.chat.title}\n\n"
            f"🎵 Music ke liye: <code>/play song name</code>\n"
            f"🎬 Video ke liye: <code>/vplay song name</code>"
        )
    except Exception:
        pass


@app.on_message(filters.video_chat_ended, group=21)
async def _vc_ended(_, m: types.Message):
    try:
        await m.reply_text(
            f"🔕 <b>Voice Chat Ended</b>\n\n"
            f"╔══════════════════╗\n"
            f"║  ⚫  OFFLINE  ⚫  ║\n"
            f"╚══════════════════╝\n\n"
            f"💬 <b>Chat:</b> {m.chat.title}\n\n"
            f"Dobara voice chat start karo aur music enjoy karo! 🎶"
        )
    except Exception:
        pass


@app.on_message(filters.video_chat_members_invited, group=22)
async def _vc_invited(_, m: types.Message):
    try:
        inviter = m.from_user.mention if m.from_user else "Someone"

        invited_users = (
            getattr(m, "invite_to_voice_chat", None)
            or getattr(m, "video_chat_invited", None)
            or getattr(m, "action", None)
        )

        users = []
        if invited_users:
            users = getattr(invited_users, "users", []) or []

        if not users:
            await m.reply_text(
                f"📨 <b>Voice Chat Invite!</b>\n\n"
                f"🎤 <b>{inviter}</b> ne kisi ko VC mein invite kiya!\n\n"
                f"Voice Chat join karo aur music enjoy karo! 🎵🎶"
            )
            return

        invited_mentions = ", ".join(u.mention for u in users[:5])
        await m.reply_text(
            f"📨 <b>Voice Chat Invite!</b>\n\n"
            f"🎤 <b>{inviter}</b> ne invite kiya:\n"
            f"👥 {invited_mentions}\n\n"
            f"Voice Chat mein aao aur music enjoy karo! 🎵🎶"
        )
    except Exception:
        pass
