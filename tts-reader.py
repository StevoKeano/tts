from telethon import TelegramClient, events
import subprocess
import asyncio
import os
import re

def clean_for_tts(text):
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'`+', '', text)
    text = re.sub(r'#+\s*', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'[-*•]\s+', '', text)
    return text.strip()

def split_sentences(text):
    # Split on sentence-ending punctuation followed by whitespace or end
    parts = re.split(r'(?<=[.!?])\s+', text)
    return [p.strip() for p in parts if p.strip()]

api_id   = int(os.environ['api_id'])
api_hash = os.environ['api_hash']
client   = TelegramClient('reader', api_id, api_hash)
BOT_USERNAME = 'StevoKeano_bot'

pending  = {}       # msg_id -> asyncio.Task (debounce)
tts_proc = None     # current Popen handle

def kill_tts():
    global tts_proc
    if tts_proc and tts_proc.poll() is None:
        tts_proc.kill()
        tts_proc = None

@client.on(events.NewMessage(from_users=BOT_USERNAME))
@client.on(events.MessageEdited(from_users=BOT_USERNAME))
async def handler(event):
    global tts_proc
    msg_id = event.message.id
    text   = clean_for_tts(event.raw_text.strip())
    if not text:
        return

    # Cancel pending debounce for this message
    if msg_id in pending:
        pending[msg_id].cancel()

    # Kill any in-progress TTS immediately
    kill_tts()

    async def speak_after_delay():
        global tts_proc
        await asyncio.sleep(3)

        sentences = split_sentences(text)
        print(f"Speaking {len(sentences)} sentence(s) from msg {msg_id}")

        loop = asyncio.get_event_loop()

        for i, sentence in enumerate(sentences):
            # Check if a newer task has killed us (task cancelled)
            await asyncio.sleep(0)          # yield — lets cancellation land
            try:
                tts_proc = subprocess.Popen(
                    ['termux-tts-speak', '-s', 'music', '-l', 'en',
                     '-n', 'GB', '-r', '1.0', sentence]
                )
                # Wait without blocking the event loop
                await loop.run_in_executor(None, tts_proc.wait)
                print(f"  [{i+1}/{len(sentences)}] done: {sentence[:40]}")
            except asyncio.CancelledError:
                kill_tts()
                raise
            except Exception as e:
                print(f"TTS failed on sentence {i+1}: {e}")
                break

        # Toast shows first 30 chars of full message
        try:
            subprocess.run(['termux-toast', '-s', 'short', f"Spoken: {text[:30]}"])
        except Exception:
            pass

        if msg_id in pending:
            del pending[msg_id]

    task = asyncio.ensure_future(speak_after_delay())
    pending[msg_id] = task

async def main():
    print("Listening for messages from @StevoKeano_bot... Ctrl+C to stop")
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
