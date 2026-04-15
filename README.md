# Tekkit 2 Discord Status Bot

Ultra basic `discord.py` bot that only updates its Discord profile status with the player count for one Minecraft Tekkit 2 server.

The Minecraft address is read from `server_address.txt` every time the bot refreshes its status, so if the server URL changes you can just edit that file. No code change is needed.

## Setup

1. Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create your env file:

```bash
cp .env.example .env
```

4. Put your Discord bot token in `.env`.
5. Put your Minecraft server address in `server_address.txt`.
6. Run the bot:

```bash
python3 bot.py
```

## Discord Bot Settings

- This bot does not need message commands.
- This bot does not need privileged intents for this use case.
- Invite the bot to at least one server so you can see its profile/presence.

## Example Status

`Playing Tekkit 2 4/20 | play.example.com:25565`

If the Minecraft server cannot be reached, the status changes to:

`Playing Tekkit 2 offline | play.example.com:25565`
