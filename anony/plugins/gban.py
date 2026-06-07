import asyncio
from pyrogram import enums, errors, filters, types
from anony import app, db
from anony.helpers import utils

GBAN_DB: set = set()


@app.on_message(filters.command(["gban"]) & filters.user(app.owner))
async def _gban(_, m: types.Message):
    user = await utils.extract_user(m)
    if not user:
        return await m.reply_text(
            "❌ <b>Usage:</b> Reply to a user or\n<code>/gban @username</code>"
        )
    if user.id == app.owner:
        return await m.reply_text("❌ Apne aap ko ban nahi kar sakte!")

    GBAN_DB.add(user.id)
    sent = await m.reply_text(
        f"🔨 <b>Global Ban</b>\n\n"
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
        except errors.UserAdminInvalid:
            failed += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.4)

    await sent.edit_text(
        f"✅ <b>Global Ban Complete</b>\n\n"
        f"👤 <b>User:</b> {user.mention} (<code>{user.id}</code>)\n"
        f"✅ <b>Banned in:</b> {banned} groups\n"
        f"❌ <b>Failed:</b> {failed}\n"
        f"📊 <b>Total groups checked:</b> {len(chats)}"
    )


@app.on_message(filters.command(["ungban"]) & filters.user(app.owner))
async def _ungban(_, m: types.Message):
    user = await utils.extract_user(m)
    if not user:
        return await m.reply_text(
            "❌ <b>Usage:</b> Reply to a user or\n<code>/ungban @username</code>"
        )

    GBAN_DB.discard(user.id)
    sent = await m.reply_text(
        f"🔓 <b>Global Unban</b>\n\n"
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
        f"✅ <b>Global Unban Complete</b>\n\n"
        f"👤 <b>User:</b> {user.mention} (<code>{user.id}</code>)\n"
        f"🔓 <b>Unbanned in:</b> {unbanned} groups"
    )


@app.on_message(filters.command(["banall"]) & filters.user(app.owner) & filters.group)
async def _banall(_, m: types.Message):
    if len(m.command) < 2 or m.command[1].lower() != "confirm":
        return await m.reply_text(
            "⚠️ <b>Ban All Members</b>\n\n"
            "Yeh command is group ke <b>tamam non-admin members</b> ko ban kar dega.\n\n"
            "✅ Confirm karne ke liye:\n<code>/banall confirm</code>"
        )

    sent = await m.reply_text("🔨 Members ko ban karna shuru kar raha hun...")
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
        f"✅ <b>Ban All Complete</b>\n\n"
        f"🔨 <b>Banned:</b> {banned} members\n"
        f"⏭️ <b>Skipped (admins/bots):</b> {skipped}"
    )
