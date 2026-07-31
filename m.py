import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, BotCommand
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioVideoPiped, AudioPiped
from yt_dlp import YoutubeDL

# ---------------- CONFIGURATION ---------------- #
API_ID = 39049809  # Your Telegram API ID from my.telegram.org
API_HASH = "a1617a3873a413cdcaa10e0f20b94754"  # Your Telegram API Hash from my.telegram.org
BOT_TOKEN = "8965905071:AAGJL5-OdsjaNh4I_yMRZkTZXOSl9LMdmpc"  # Your Telegram Bot Token from @BotFather
SESSION_STRING = "BQJT2lEAlG2_rK_sB9B263W0bkXqDGAINI9XBXJ7ToYkOBSWfszCpJWM6ZpOQWP6V_RJlsD8UILN8yeFPB2czqS6NT4Tn3JWivSxRiYF0jeDkniPOi8GBUlfiZ6xH1l9-ih-g4Py119mSuefrsc_V8h8eqX9ZoNU3eu08au2WkvkX0uS6NjB8OKDP0wevg0DYLyonZOHDxWgWCaUrxomIlfEcGJi_usqB4Nyh-4s4Q1aVXaZELj-_K5-0BjC9JsgnTu22g_vu4wtCra9QQ6H0rTOheaZyztggPa9-buEDy3KNchO-9avEeawpN3w3Ja2uiV1fEyyHQm2mmo15Zxv3c5Xf0GCaQAAAAGSj2-vAA"  # Pyrogram String Session

# Specific Bot Owner User ID
BOT_OWNER_ID = 7455934081  # Replace with your Telegram User ID

# Authorized Group IDs allowed to use this bot
ALLOWED_GROUPS = [-1002359917093]  # Put your target group IDs here
# ----------------------------------------------- #

app = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user_app = Client("user_session", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
call_py = PyTgCalls(user_app)


async def is_admin_or_owner(chat_id: int, user_id: int) -> bool:
    """Check if the user is the Bot Owner, Group Creator, or Group Admin."""
    if user_id == BOT_OWNER_ID:
        return True
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in ["administrator", "creator"]
    except Exception:
        return False


def get_yt_stream(query: str, video: bool = False):
    """Search YouTube and return playable stream URL and Title."""
    ydl_opts = {
        "format": "bestvideo+bestaudio/best" if video else "bestaudio/best",
        "quiet": True,
        "default_search": "ytsearch",
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        if "entries" in info:
            info = info["entries"][0]
        return info["url"], info.get("title", "Unknown Stream")


@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message: Message):
    bot_user = await client.get_me()
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Add Me To Your Group", url=f"https://t.me/{bot_user.username}?startgroup=true")]
    ])
    await message.reply_text(
        "Hello! I am a Telegram Voice & Video Streaming Bot.\n\n"
        "Available Commands:\n"
        "/join - Join group voice chat\n"
        "/playm <song> - Play YouTube audio stream\n"
        "/playv <video> - Play YouTube video with screen share\n"
        "/stop - Stop active stream or screen share\n"
        "/skip5s - Skip forward 5 seconds\n"
        "/skip10s - Skip forward 10 seconds\n"
        "/undo5s - Rewind 5 seconds\n"
        "/undo10s - Rewind 10 seconds\n\n"
        "Click the button below to add me to your group!",
        reply_markup=keyboard
    )


@app.on_message(filters.command("join") & filters.group)
async def join_vc(client, message: Message):
    if message.chat.id not in ALLOWED_GROUPS:
        return await message.reply_text("This group is not authorized to use this bot.")

    if not await is_admin_or_owner(message.chat.id, message.from_user.id):
        return await message.reply_text("Only group admins or bot owner can use this command.")

    try:
        await user_app.join_chat(message.chat.id)
    except Exception:
        pass

    await message.reply_text("Successfully connected helper userbot to the chat!")


@app.on_message(filters.command("playm") & filters.group)
async def play_audio_stream(client, message: Message):
    if message.chat.id not in ALLOWED_GROUPS:
        return await message.reply_text("This group is not authorized to use this bot.")

    if not await is_admin_or_owner(message.chat.id, message.from_user.id):
        return await message.reply_text("Only group admins or bot owner can use this command.")

    if len(message.command) < 2:
        return await message.reply_text("Usage: /playm <song name>")

    query = message.text.split(None, 1)[1]
    status_msg = await message.reply_text("Searching YouTube for audio...")

    try:
        stream_url, title = get_yt_stream(query, video=False)
        await call_py.play(message.chat.id, AudioPiped(stream_url))
        await status_msg.edit_text(f"**Now Playing Audio:** {title}")
    except Exception as e:
        await status_msg.edit_text(f"Error playing audio stream: {e}")


@app.on_message(filters.command("playv") & filters.group)
async def play_video_stream(client, message: Message):
    if message.chat.id not in ALLOWED_GROUPS:
        return await message.reply_text("This group is not authorized to use this bot.")

    if not await is_admin_or_owner(message.chat.id, message.from_user.id):
        return await message.reply_text("Only group admins or bot owner can use this command.")

    if len(message.command) < 2:
        return await message.reply_text("Usage: /playv <video name>")

    query = message.text.split(None, 1)[1]
    status_msg = await message.reply_text("Searching YouTube for video...")

    try:
        stream_url, title = get_yt_stream(query, video=True)
        await call_py.play(message.chat.id, AudioVideoPiped(stream_url))
        await status_msg.edit_text(f"**Now Streaming Video:** {title}")
    except Exception as e:
        await status_msg.edit_text(f"Error playing video stream: {e}")


@app.on_message(filters.command("stop") & filters.group)
async def stop_stream(client, message: Message):
    if message.chat.id not in ALLOWED_GROUPS:
        return await message.reply_text("This group is not authorized to use this bot.")

    if not await is_admin_or_owner(message.chat.id, message.from_user.id):
        return await message.reply_text("Only group admins or bot owner can use this command.")

    try:
        await call_py.leave_call(message.chat.id)
        await message.reply_text("Streaming stopped and screen share closed successfully.")
    except Exception as e:
        await message.reply_text(f"Failed to stop streaming: {e}")


@app.on_message(filters.command(["skip5s", "skip10s", "undo5s", "undo10s"]) & filters.group)
async def seek_control(client, message: Message):
    if message.chat.id not in ALLOWED_GROUPS:
        return await message.reply_text("This group is not authorized to use this bot.")

    if not await is_admin_or_owner(message.chat.id, message.from_user.id):
        return await message.reply_text("Only group admins or bot owner can use this command.")

    cmd = message.command[0]
    seconds = 5 if "5s" in cmd else 10
    is_forward = "skip" in cmd

    try:
        active_call = await call_py.get_active_call(message.chat.id)
        current_time = active_call.played_time
        target_time = current_time + seconds if is_forward else max(0, current_time - seconds)

        await call_py.seek_stream(message.chat.id, target_time)
        action = "Skipped forward" if is_forward else "Rewound"
        await message.reply_text(f"{action} {seconds} seconds successfully.")
    except Exception as e:
        await message.reply_text(f"Failed to seek stream: {e}")


async def setup_bot_commands():
    """Set bot menu commands for Telegram interface auto-complete."""
    commands = [
        BotCommand("start", "Start the bot and get info"),
        BotCommand("join", "Connect bot to group voice chat"),
        BotCommand("playm", "Play YouTube audio stream"),
        BotCommand("playv", "Play YouTube video stream with screen share"),
        BotCommand("stop", "Stop active live stream or audio"),
        BotCommand("skip5s", "Skip forward 5 seconds"),
        BotCommand("skip10s", "Skip forward 10 seconds"),
        BotCommand("undo5s", "Rewind 5 seconds"),
        BotCommand("undo10s", "Rewind 10 seconds"),
    ]
    await app.set_bot_commands(commands)


async def main():
    await user_app.start()
    await app.start()
    await call_py.start()
    await setup_bot_commands()
    print("Bot is up and running successfully!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())