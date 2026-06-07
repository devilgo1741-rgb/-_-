import asyncio
from pyrogram import enums, errors, filters, types
from anony import app
from anony.helpers import utils

GBAN_DB: set = set()


@app.on_message(filters.command(["gban"]) & filters.user(app.owner))
async def _gban(_, m: types.Message):
    user = await utils.extract_user(m)
    if not user:
        return await m.reply_text(
            "❌ <b>Usage:</b> Reply to a user or use\n<code>/gban @username</code>"
        )

    if user.id == app.owner:
        return await m.reply_text("❌ Apne aap ko global ban nahi kar sakte!")

    if user.id in GBAN_DB:
        return await m.reply_text(f"⚠️ {user.mention} pehle se globally banned hai.")

    GBAN_DB.add(user.id)
    sent = await m.reply_text(
        f"🔨 <b>Global Ban</b>\n\n"
        f"👤 <b>User:</b> {user.mention} (<code>{user.id}</code>)\n"
        f"⏳ Tamam groups mein ban kar raha hun..."
    )

    banned, failed, total = 0, 0, 0

    async for dialog in app.get_dialogs():
        if dialog.chat.type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            continue
        total += 1
        try:
            me = await app.get_chat_member(dialog.chat.id, app.id)
            if me.status != enums.ChatMemberStatus.ADMINISTRATOR:
                continue
            await app.ban_chat_member(dialog.chat.id, user.id)
            banned += 1
        except errors.UserAdminInvalid:
            failed += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.5)

    await sent.edit_text(
        f"✅ <b>Global Ban Complete</b>\n\n"
        f"👤 <b>User:</b> {user.mention} (<code>{user.id}</code>)\n"
        f"✅ <b>Banned:</b> {banned} groups\n"
        f"❌ <b>Failed:</b> {failed} groups\n"
        f"📊 <b>Total checked:</b> {total}"
    )


@app.on_message(filters.command(["ungban"]) & filters.user(app.owner))
async def _ungban(_, m: types.Message):
    user = await utils.extract_user(m)
    if not user:
        return await m.reply_text(
            "❌ <b>Usage:</b> Reply to a user or use\n<code>/ungban @username</code>"
        )

    if user.id not in GBAN_DB:
        return await m.reply_text(f"⚠️ {user.mention} globally banned nahi hai.")

    GBAN_DB.discard(user.id)
    sent = await m.reply_text(
        f"🔓 <b>Global Unban</b>\n\n"
        f"👤 <b>User:</b> {user.mention}\n"
        f"⏳ Tamam groups mein unban kar raha hun..."
    )

    unbanned, total = 0, 0

    async for dialog in app.get_dialogs():
        if dialog.chat.type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            continue
        total += 1
        try:
            await app.unban_chat_member(dialog.chat.id, user.id)
            unbanned += 1
        except Exception:
            pass
        await asyncio.sleep(0.5)

    await sent.edit_text(
        f"✅ <b>Global Unban Complete</b>\n\n"
        f"👤 <b>User:</b> {user.mention} (<code>{user.id}</code>)\n"
        f"🔓 <b>Unbanned:</b> {unbanned} groups"
    )


@app.on_message(filters.command(["banall"]) & filters.user(app.owner) & filters.group)
async def _banall(_, m: types.Message):
    sent = await m.reply_text(
        "⚠️ <b>Ban All Members?</b>\n\n"
        "Yeh command is group ke tamam non-admin members ko ban kar dega.\n\n"
        "Confirm karne ke liye 30 second mein <code>/banall confirm</code> bhejo."
    )

    if len(m.command) > 1 and m.command[1].lower() == "confirm":
        await sent.delete()
        await _do_banall(m)
        return

    await asyncio.sleep(30)
    try:
        await sent.delete()
    except Exception:
        pass


async def _do_banall(m: types.Message):
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
        f"✅ <b>Ban All Complete</b>\n\n"
        f"🔨 <b>Banned:</b> {banned} members\n"
        f"⏭️ <b>Skipped (admins/bots):</b> {skipped}"
    )
