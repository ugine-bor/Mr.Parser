# Mr.Parser - Discord Bot

![GitHub last commit](https://img.shields.io/github/last-commit/ugine-bor/Mr.Parser)
[![Discord.py](https://img.shields.io/badge/discord.py-2.0%2B-blue)](https://discordpy.readthedocs.io/)

A multifunctional Discord bot with various features including web scraping, text game, voice capabilities, and rich presence integration.

## Features

- **Habr.com Integration**
  - Latest tech articles
  - Multiple recent posts
- **SCP Foundation**
  - Latest translations
  - Random SCP entries
- **Interactive Text Game**
  - Branching narrative
  - Multiple endings
- **Voice Channel Features**
  - Music playback
  - Voice message transcription
  - Text-to-Speech (TTS)
- **Rich Presence**
  - Custom status
  - Profile buttons
- **Administration Tools**
  - Nickname management
  - Interactive menus

## Installation

1. **Clone repository**
   ```bash
   git clone https://github.com/ugine-bor/Mr.Parser.git
   cd Mr.Parser
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **FFmpeg Setup**  
   Place FFmpeg executables (`ffmpeg.exe`, `ffplay.exe`, `ffprobe.exe`) in project root

4. **Environment Variables**  
   Create `.env` file with:
   ```env
   DISCORD_TOKEN=your_bot_token
   ID=your_application_id
   HE=your_user_id
   ```

## Commands

| Command     | Description                          |
|-------------|--------------------------------------|
| `;start`    | Show main interactive menu           |
| `;article`  | Get latest Habr article              |
| `;articles` | Get multiple recent Habr articles    |
| `;scp`      | Show latest SCP translations         |
| `;rscp`     | Get random SCP entry                 |
| `;vc`       | Voice channel controls               |
| `;chngnm`   | Change user nickname (Admin only)    |

## Text Game Features

```python
textgame.py
├─ Branching narrative system
├─ Random event outcomes
├─ Multiple endings
├─ Save state management
└─ Interactive buttons interface
```

**Game Components:**
- `states.json` - Game state configuration
- `engine.py` - Game engine (external repository)

More about textgame engine: [TextGame repository](https://github.com/ugine-bor/TextGame)

## Voice Features

- Automatic voice message transcription
- MP3/WAV conversion
- Music playback controls:
  - Play/Pause
  - Resume
  - Disconnect

## Configuration

**Required Intents:**
```python
intents = discord.Intents.all()
```

**Permissions:**
- Manage Nicknames
- Connect to Voice
- Send Messages
- Embed Links
