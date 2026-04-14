from telethon import TelegramClient, events
import subprocess  # For Termux-API TTS call
import asyncio
import os

api_id = int(os.environ['api_id'])      # integer from my.telegram.org
api_hash = os.environ['api_hash']

client = TelegramClient('reader', api_id, api_hash)

# Optional: Only react to messages from this bot (or remove filter for all)
BOT_USERNAME = 'StevoKeano_bot'  # or 'username' without @

@client.on(events.NewMessage(from_users=BOT_USERNAME))
async def handler(event):
    text = event.raw_text.strip()
    if not text:
        return  # Skip empty

    print(f"New message from @{BOT_USERNAME}: {text}")

    # Speak aloud using Termux-API TTS (native Android engine)
    # Speak aloud using music stream (reliable in background)
    try:
      subprocess.run(['termux-tts-speak', '-s', 'music', '-l', 'en', '-n', 'GB', '-r', '1.0', text], check=True)
#      subprocess.run(['termux-toast', '-s', 'short', f"Spoken: {text}"])
      print("✅ Spoken via MUSIC stream (GB)")
    except Exception as e:
        print(f"TTS failed: {e}")
        # Reliable fallback (always works)
        from gtts import gTTS
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save("/sdcard/Download/temp_message.mp3")
        subprocess.run(['termux-media-player', 'play', '/sdcard/Download/temp_message.mp3'])
        print("✅ Spoken via gTTS fallback")

async def main():
    print("Listening for messages from @StevoKeano_bot... Ctrl+C to stop")
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
