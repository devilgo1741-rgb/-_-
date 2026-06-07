import asyncio
import os
import subprocess
from datetime import datetime

from pyrogram import filters, types
from anony import app, config


GITHUB_PAT = os.getenv("GITHUB_PAT", "")
REPO_URL = f"https://devilgo1741-rgb:{GITHUB_PAT}@github.com/devilgo1741-rgb/-_-.git"


def _git_push() -> tuple[bool, str]:
    try:
        result = subprocess.run(
            ["git", "push", REPO_URL, "master"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            return True, result.stdout or "Pushed successfully."
        return False, result.stderr or "Unknown error."
    except subprocess.TimeoutExpired:
        return False, "Git push timed out."
    except Exception as e:
        return False, str(e)


async def _auto_push():
    await asyncio.sleep(15)
    try:
        ok, msg = await asyncio.get_event_loop().run_in_executor(None, _git_push)
        if ok:
            await app.send_message(
                config.LOGGER_ID,
                f"✅ <b>Auto GitHub Sync</b>\n"
                f"🕐 {datetime.now().strftime('%d %b %Y %H:%M:%S')}\n"
                f"📤 All changes pushed to GitHub on startup.",
            )
    except Exception:
        pass


asyncio.get_event_loop().create_task(_auto_push())


@app.on_message(filters.command(["gitpush", "gitsync"]))
async def _gitpush(_, m: types.Message):
    if not m.from_user or m.from_user.id != config.OWNER_ID:
        return

    sent = await m.reply_text(
        "📤 <b>GitHub Sync</b>\n\n⏳ Changes push kar raha hun..."
    )

    ok, output = await asyncio.get_event_loop().run_in_executor(None, _git_push)

    if ok:
        await sent.edit_text(
            f"✅ <b>GitHub Sync Complete!</b>\n\n"
            f"🕐 <b>Time:</b> {datetime.now().strftime('%d %b %Y %H:%M:%S')}\n"
            f"🔗 <b>Repo:</b> github.com/devilgo1741-rgb/-_-\n"
            f"📤 Tamam changes push ho gaye!"
        )
    else:
        await sent.edit_text(
            f"❌ <b>GitHub Sync Failed!</b>\n\n"
            f"<code>{output[:500]}</code>"
        )
