# TTS-Speak for Telegram (Termux)

Listens for messages from a Telegram bot and speaks them aloud on Android using Termux-API TTS with a British English voice.

## Features

- Monitors a specified Telegram bot for new messages
- Speaks messages aloud via native Android TTS (Google TTS, en-GB)
- Runs in background via `nohup`
- gTTS fallback if native TTS fails

## Requirements

- [Termux](https://termux.dev)
- [Termux:API](https://wiki.termux.com/wiki/Termux:API) app installed
- Google TTS with English (United Kingdom) voice pack installed

## Install

```bash
pkg install python termux-api
pip install telethon gtts
Configuration
Edit tts-reader.py and set your credentials:
api_id = YOUR_API_ID
api_hash = 'YOUR_API_HASH'
BOT_USERNAME = 'your_bot_username'
Run
nohup python3 tts-reader.py >> reader.log 2>&1 &
Voice
Uses Google TTS with British English (en-GB) via termux-tts-speak.
To change voice region edit this line in the script:
termux-tts-speak -s music -l en -n GB -r 1.0
Author
StevoKeano
