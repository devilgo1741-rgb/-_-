from pyrogram import filters, types
from anony import app, config


OWNER_CMDS = """
👑 <b>Owner Commands</b>

🔴 <b>Bot Control:</b>
• /sleep — Bot ko sleep mode mein daalo
• /sleep off — Bot ko wapas active karo
• /maintenance — Maintenance mode on karo
• /maintenance off — Maintenance mode off karo
• /restart — Bot restart karo

🔨 <b>Ban Commands:</b>
• /gban [user] — User ko sabhi groups se ban karo
• /ungban [user] — User ka global ban hatao
• /banall confirm — Group ke tamam members ko ban karo

👥 <b>Admin Management:</b>
• /addsudo [user] — Sudo user add karo
• /rmsudo [user] — Sudo user remove karo
• /sudolist — Sudo users ki list dekho
• /blacklist [id] — Chat/user blacklist karo
• /unblacklist [id] — Blacklist se hatao

📊 <b>Bot Info:</b>
• /logs — Log file bhejo
• /logger on/off — Logger toggle karo
• /activevc — Active voice chats dekho
• /broadcast — Tamam groups mein message bhejo
• /eval — Code execute karo
"""

USER_CMDS = """
🎵 <b>Play Commands</b>
• /play [song/url] — Audio play karo
• /vplay [song/url] — Video play karo
• /playforce [song] — Force play karo
• /vplayforce [song] — Force video play karo

⏯️ <b>Playback Controls</b>
• /pause — Stream pause karo
• /resume — Stream resume karo
• /skip — Current track skip karo
• /stop / /end — Streaming band karo
• /loop [count] — Loop set karo
• /seek [seconds] — Aage seekaro
• /seekback [seconds] — Peeche seekaro
• /replay — Current track dobara chalao
• /queue — Queue dekho

ℹ️ <b>Info Commands</b>
• /start — Bot start karo
• /help — Help menu dekho
• /ping / /alive — Ping check karo
• /stats — Bot stats dekho
• /sudolist — Sudo list dekho

⚙️ <b>Settings</b>
• /settings / /playmode — Group settings
• /lang — Language change karo
• /auth [user] — User authorize karo
• /unauth [user] — Authorization hatao
• /authlist — Authorized users dekho
• /reload / /admincache — Admin cache refresh karo
"""


@app.on_message(
    filters.command(["cmds", "commands", "cmdlist"])
)
async def _commands(_, m: types.Message):
    is_owner = m.from_user and m.from_user.id == config.OWNER_ID

    if is_owner:
        await m.reply_text(OWNER_CMDS)
        await m.reply_text(USER_CMDS)
    else:
        await m.reply_text(USER_CMDS)
