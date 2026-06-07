from pyrogram import filters, types
from anony import app, config


OWNER_CMDS = (
    "👑 <b>Owner Commands</b>\n"
    "━━━━━━━━━━━━━━━━━━━\n\n"
    "🔴 <b>Bot Control:</b>\n"
    "• /sleep — Sleep mode on\n"
    "• /sleep off — Sleep mode off\n"
    "• /maintenance — Maintenance on\n"
    "• /maintenance off — Maintenance off\n"
    "• /restart — Bot restart karo\n\n"
    "🔨 <b>Ban Commands:</b>\n"
    "• /gban [user] — All groups se ban karo\n"
    "• /ungban [user] — Global ban hatao\n"
    "• /banall confirm — Group ke sab members ban karo\n\n"
    "👥 <b>User Management:</b>\n"
    "• /addsudo [user] — Sudo add karo\n"
    "• /rmsudo [user] — Sudo hatao\n"
    "• /sudolist — Sudo list dekho\n"
    "• /blacklist [id] — Blacklist mein daalo\n"
    "• /unblacklist [id] — Blacklist se hatao\n\n"
    "📢 <b>Broadcast:</b>\n"
    "• /broadcast — Groups + Users ko bhejo\n"
    "• /broadcast -nochat — Sirf Users\n"
    "• /broadcast -nouser — Sirf Groups\n"
    "• /broadcast -copy — Forward tag hatao\n\n"
    "📊 <b>Info & Logs:</b>\n"
    "• /activevc — Active voice chats\n"
    "• /ac — Active VC count\n"
    "• /logs — Log file bhejo\n"
    "• /logger on/off — Logger toggle\n"
    "• /eval — Code run karo\n"
)

USER_CMDS = (
    "🎵 <b>Play Commands</b>\n"
    "━━━━━━━━━━━━━━━━━━━\n"
    "• /play [song/url] — Audio play karo\n"
    "• /vplay [song/url] — Video play karo\n"
    "• /playforce [song] — Force play\n"
    "• /vplayforce [song] — Force video play\n\n"
    "⏯️ <b>Playback Controls</b>\n"
    "━━━━━━━━━━━━━━━━━━━\n"
    "• /pause — Pause karo\n"
    "• /resume — Resume karo\n"
    "• /skip — Next track\n"
    "• /stop / /end — Stop karo\n"
    "• /loop [count] — Loop set karo\n"
    "• /seek [seconds] — Aage jao\n"
    "• /seekback [seconds] — Peeche jao\n"
    "• /replay — Dobara chalao\n"
    "• /queue — Queue dekho\n\n"
    "⚙️ <b>Group Settings</b>\n"
    "━━━━━━━━━━━━━━━━━━━\n"
    "• /settings / /playmode — Settings\n"
    "• /lang — Language change karo\n"
    "• /auth [user] — User authorize karo\n"
    "• /unauth [user] — Authorization hatao\n"
    "• /authlist — Authorized users\n"
    "• /reload — Admin cache refresh\n\n"
    "ℹ️ <b>Info Commands</b>\n"
    "━━━━━━━━━━━━━━━━━━━\n"
    "• /start — Bot start karo\n"
    "• /help — Help menu\n"
    "• /ping / /alive — Ping check\n"
    "• /stats — Bot stats\n"
    "• /sudolist — Sudo list\n"
    "• /cmds — Yeh list! 😄\n"
)


@app.on_message(filters.command(["cmds", "commands", "cmdlist"]))
async def _commands(_, m: types.Message):
    is_owner = m.from_user and m.from_user.id == config.OWNER_ID
    if is_owner:
        await m.reply_text(OWNER_CMDS)
    await m.reply_text(USER_CMDS)
