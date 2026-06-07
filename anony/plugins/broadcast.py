import os
import asyncio

from pyrogram import errors, filters, types

from anony import app, db, lang


broadcasting = asyncio.Lock()

@app.on_message(filters.command(["broadcast"]) & app.sudoers)
@lang.language()
async def _broadcast(_, message: types.Message):
    if not message.reply_to_message:
        return await message.reply_text(message.lang["gcast_usage"])

    if broadcasting.locked():
        return await message.reply_text(message.lang["gcast_active"])

    msg = message.reply_to_message
    copy = "-copy" in message.command
    count, ucount = 0, 0
    groups, users = set(), set()

    if "-nochat" not in message.command:
        groups = set(await db.get_chats())
    if "-nouser" not in message.command:
        users = set(await db.get_users())

    chats = list(groups | users)
    total = len(chats)

    sent = await message.reply_text(
        f"📢 <b>Broadcast Starting</b>\n\n"
        f"👥 <b>Groups:</b> <code>{len(groups)}</code>\n"
        f"👤 <b>Users (DM):</b> <code>{len(users)}</code>\n"
        f"📊 <b>Total reach:</b> <code>{total}</code>\n\n"
        f"⏳ Broadcasting..."
    )

    failed = None
    done = 0

    async with broadcasting:
        for chat in chats:
            try:
                (
                    await msg.copy(chat, reply_markup=msg.reply_markup)
                    if copy
                    else await msg.forward(chat)
                )
                if chat in groups:
                    count += 1
                else:
                    ucount += 1
                done += 1

                if done % 20 == 0:
                    try:
                        await sent.edit_text(
                            f"📢 <b>Broadcasting...</b>\n\n"
                            f"✅ <b>Sent:</b> <code>{done}/{total}</code>\n"
                            f"👥 <b>Groups:</b> <code>{count}</code>\n"
                            f"👤 <b>Users:</b> <code>{ucount}</code>"
                        )
                    except Exception:
                        pass

                await asyncio.sleep(0.2)
            except errors.FloodWait as fw:
                await asyncio.sleep(fw.value + 10)
            except Exception as ex:
                if not failed:
                    failed = open("errors.txt", "w")
                failed.write(f"{chat} - {ex}\n")
                continue

    result_text = (
        f"✅ <b>Broadcast Complete!</b>\n\n"
        f"👥 <b>Groups sent:</b> <code>{count}</code>\n"
        f"👤 <b>Users sent:</b> <code>{ucount}</code>\n"
        f"📊 <b>Total reached:</b> <code>{count + ucount}</code>\n"
        f"❌ <b>Failed:</b> <code>{total - count - ucount}</code>"
    )

    if failed:
        failed.close()
        await message.reply_document(document="errors.txt", caption=result_text)
        try:
            os.remove("errors.txt")
        except Exception:
            pass

    await sent.edit_text(result_text)
