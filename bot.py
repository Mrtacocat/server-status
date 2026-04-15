import logging
import os
from pathlib import Path
from typing import Optional

import discord
from discord.ext import tasks
from dotenv import load_dotenv
from mcstatus import JavaServer


load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
LOGGER = logging.getLogger("tekkit-status-bot")

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
STATUS_UPDATE_SECONDS = int(os.getenv("STATUS_UPDATE_SECONDS", "60"))
MC_TIMEOUT_SECONDS = float(os.getenv("MC_TIMEOUT_SECONDS", "5"))
SERVER_FILE = Path(os.getenv("MINECRAFT_SERVER_FILE", "server_address.txt"))


def trim_activity(text: str, limit: int = 128) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def read_server_address() -> str:
    if not SERVER_FILE.exists():
        return ""

    for raw_line in SERVER_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line and not line.startswith("#"):
            return line

    return ""


class TekkitStatusBot(discord.Client):
    def __init__(self) -> None:
        intents = discord.Intents.none()
        super().__init__(
            intents=intents,
            activity=discord.Game(name="Tekkit 2 status starting..."),
        )
        self.last_activity_name: Optional[str] = None

    async def setup_hook(self) -> None:
        self.update_presence.start()

    async def on_ready(self) -> None:
        if self.user is None:
            return
        LOGGER.info("Logged in as %s (%s)", self.user, self.user.id)

    @tasks.loop(seconds=STATUS_UPDATE_SECONDS)
    async def update_presence(self) -> None:
        address = read_server_address()
        activity_name = await self.build_activity_name(address)
        await self.set_activity(activity_name)

    @update_presence.before_loop
    async def before_update_presence(self) -> None:
        await self.wait_until_ready()

    async def build_activity_name(self, address: str) -> str:
        if not address:
            return "Add a server to server_address.txt"

        try:
            server = await JavaServer.async_lookup(address, timeout=MC_TIMEOUT_SECONDS)
            status = await server.async_status()
            online = status.players.online
            max_players = status.players.max
            return trim_activity(f"Tekkit 2 {online}/{max_players} | {address}")
        except Exception as exc:
            LOGGER.warning("Could not fetch status for %s: %s", address, exc)
            return trim_activity(f"Tekkit 2 offline | {address}")

    async def set_activity(self, activity_name: str) -> None:
        if activity_name == self.last_activity_name:
            return

        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Game(name=activity_name),
        )
        self.last_activity_name = activity_name
        LOGGER.info("Presence updated: %s", activity_name)


def main() -> None:
    if not DISCORD_TOKEN:
        raise RuntimeError("DISCORD_TOKEN is missing. Set it in your .env file.")

    bot = TekkitStatusBot()
    bot.run(DISCORD_TOKEN, log_handler=None)


if __name__ == "__main__":
    main()
