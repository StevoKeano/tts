from telethon import TelegramClient, events
import subprocess  # For Termux-API TTS call
import asyncio
import os
import re

def clean_for_tts(text):
    text = re.sub(r'\*+', '', text)        # bold/italic
    text = re.sub(r'`+', '', text)         # code ticks
    text = re.sub(r'#+\s*', '', text)      # headers
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # links
    text = re.sub(r'[-*•]\s+', '', text)   # bullets
    return text.strip()

api_id = int(os.environ['api_id'])      # integer from my.telegram.org
api_hash = os.environ['api_hash']

client = TelegramClient('reader', api_id, api_hash)

# Optional: Only react to messages from this bot (or remove filter for all)
BOT_USERNAME = 'StevoKeano_bot'  # or 'username' without @
pending = {}
@client.on(events.NewMessage(from_users=BOT_USERNAME))
@client.on(events.MessageEdited(from_users=BOT_USERNAME))
async def handler(event):
    msg_id = event.message.id
    text = clean_for_tts(event.raw_text.strip())
    if not text:
        return

    if msg_id in pending:
        pending[msg_id].cancel()

    async def speak_after_delay():
        await asyncio.sleep(3)
        print(f"New message from @{BOT_USERNAME}: {text}")
        print(f"TEXT_LENGTH={len(text)}")
        with open('/sdcard/Download/tts_input.txt', 'w') as f:
            f.write(text)
        try:
#            subprocess.run(['termux-tts-speak', '-s', 'music', '-l', 'en', '-n', 'GB', '-r', '1.0', '-f', '/sdcard/Download/tts_input.txt'], check=True)
            subprocess.run(['termux-tts-speak', '-s', 'music', '-l', 'en', '-n', 'GB', '-r', '1.0', text], check=True)
            subprocess.run(['termux-toast', '-s', 'short', f"Spoken: {text[:30]}"])
            print("✅ Spoken via MUSIC stream (GB)")
        except Exception as e:
            print(f"TTS failed: {e}")
        if msg_id in pending:
            del pending[msg_id]

    pending[msg_id] = asyncio.ensure_future(speak_after_delay())
async def main():
    print("Listening for messages from @StevoKeano_bot... Ctrl+C to stop")
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
