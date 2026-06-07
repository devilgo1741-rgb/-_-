import asyncio
from pyrogram import enums, filters, types
from anony import app, config, db
from anony.helpers import utils

GBAN_DB: set = set()


@app.on_message(filters.command(["gban"]))
async def _gban(_, m: types.Message):
    if not m.from_user or m.from_user.id != config.OWNER_ID:
        return

    user = await utils.extract_user(m)
    if not user:
        return await m.reply_text(
            "❌ <b>Usage:</b>\nReply to a user or <code>/gban @username</code>"
        )
    if user.id == config.OWNER_ID:
        return await m.reply_text("❌ Apne aap ko ban nahi kar sakte!")

    GBAN_DB.add(user.id)
    sent = await m.reply_text(
        f"🔨 <b>Global Ban Starting...</b>\n\n"
        f"👤 <b>User:</b> {user.mention} (<code>{user.id}</code>)\n"
        f"⏳ Tamam groups mein ban kar raha hun..."
    )

    banned, failed = 0, 0
    chats = await db.get_chats()

    for chat_id in chats:
        try:
            me = await app.get_chat_member(chat_id, app.id)
            if me.status != enums.ChatMemberStatus.ADMINISTRATOR:
                continue
            await app.ban_chat_member(chat_id, user.id)
            banned += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.4)

    await sent.edit_text(
        f"✅ <b>Global Ban Complete!</b>\n\n"
        f"👤 <b>User:</b> {user.mention} (<code>{user.id}</code>)\n"
        f"✅ <b>Banned in:</b> <code>{banned}</code> groups\n"
        f"❌ <b>Failed:</b> <code>{failed}</code>\n"
        f"📊 <b>Total checked:</b> <code>{len(chats)}</code>"
    )


@app.on_message(filters.command(["ungban"]))
async def _ungban(_, m: types.Message):
    if not m.from_user or m.from_user.id != config.OWNER_ID:
        return

    user = await utils.extract_user(m)
    if not user:
        return await m.reply_text(
            "❌ <b>Usage:</b>\nReply to a user or <code>/ungban @username</code>"
        )

    GBAN_DB.discard(user.id)
    sent = await m.reply_text(
        f"🔓 <b>Global Unban Starting...</b>\n\n"
        f"👤 <b>User:</b> {user.mention}\n"
        f"⏳ Tamam groups mein unban kar raha hun..."
    )

    unbanned = 0
    chats = await db.get_chats()

    for chat_id in chats:
        try:
            await app.unban_chat_member(chat_id, user.id)
            unbanned += 1
        except Exception:
            pass
        await asyncio.sleep(0.4)

    await sent.edit_text(
        f"✅ <b>Global Unban Complete!</b>\n\n"
        f"👤 <b>User:</b> {user.mention} (<code>{user.id}</code>)\n"
        f"🔓 <b>Unbanned in:</b> <code>{unbanned}</code> groups"
    )


@app.on_message(filters.command(["banall"]) & filters.group)
async def _banall(_, m: types.Message):
    if not m.from_user or m.from_user.id != config.OWNER_ID:
        return

    if len(m.command) < 2 or m.command[1].lower() != "confirm":
        return await m.reply_text(
            "⚠️ <b>Ban All Members</b>\n\n"
            "Yeh command is group ke <b>tamam non-admin members</b> ko ban kar dega.\n\n"
            "✅ Confirm karne ke liye:\n<code>/banall confirm</code>"
        )

    sent = await m.reply_text("🔨 Sab members ko ban karna shuru kar raha hun...")
    banned, skipped = 0, 0

    async for member in app.get_chat_members(m.chat.id):
        if member.status in [
            enums.ChatMemberStatus.ADMINISTRATOR,
            enums.ChatMemberStatus.OWNER,
        ]:
            skipped += 1
            continue
        if member.user.is_bot:
            skipped += 1
            continue
        try:
            await app.ban_chat_member(m.chat.id, member.user.id)
            banned += 1
        except Exception:
            skipped += 1
        await asyncio.sleep(0.3)

    await sent.edit_text(
        f"✅ <b>Ban All Complete!</b>\n\n"
        f"🔨 <b>Banned:</b> <code>{banned}</code> members\n"
        f"⏭️ <b>Skipped (admins/bots):</b> <code>{skipped}</code>"
    )
