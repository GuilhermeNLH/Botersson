"""Botersson – Discord Research Assistant Bot.

Entry point: python bot/main.py
"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

import discord
from discord.ext import commands, tasks
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import BotConfig, SchedulerConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s – %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("botersson")

# ─── Bot setup ────────────────────────────────────────────────────────────────

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True


class Botersson(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=BotConfig.PREFIX,
            description=BotConfig.DESCRIPTION,
            intents=intents,
            help_command=commands.DefaultHelpCommand(),
        )
        self.scheduler = AsyncIOScheduler()

    async def setup_hook(self) -> None:
        """Load all cogs and sync slash commands."""
        cogs = ["bot.cogs.search", "bot.cogs.patents", "bot.cogs.ai", "bot.cogs.excel"]
        for cog in cogs:
            try:
                await self.load_extension(cog)
                log.info("Loaded cog: %s", cog)
            except Exception as exc:
                log.error("Failed to load cog %s: %s", cog, exc)

        # Sync slash commands
        if BotConfig.GUILD_ID:
            guild = discord.Object(id=BotConfig.GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        else:
            await self.tree.sync()

        # Start scheduler
        if SchedulerConfig.ENABLED:
            self._setup_scheduler()
            self.scheduler.start()
            log.info("Scheduler started")

    def _setup_scheduler(self) -> None:
        from bot.services import excel_manager

        @self.scheduler.scheduled_job("cron", hour=SchedulerConfig.DAILY_HOUR, minute=0)
        async def daily_summary() -> None:
            """Send a daily summary to all guilds."""
            summary = excel_manager.get_all_sheets_summary()
            total = sum(summary.values())
            if total == 0:
                return
            for guild in self.guilds:
                # Try to find a suitable channel
                channel = None
                for ch in guild.text_channels:
                    if ch.permissions_for(guild.me).send_messages:
                        channel = ch
                        break
                if channel:
                    embed = discord.Embed(
                        title="📊 Daily Research Summary",
                        color=discord.Color.blue(),
                    )
                    for name, count in summary.items():
                        embed.add_field(name=name, value=str(count), inline=True)
                    embed.set_footer(text=f"Total: {total} records | Botersson")
                    try:
                        await channel.send(embed=embed)
                    except Exception as exc:  # noqa: BLE001
                        log.warning("Could not send daily summary to %s: %s", guild.name, exc)

    async def on_ready(self) -> None:
        log.info("Logged in as %s (ID: %s)", self.user, self.user.id)
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=BotConfig.ACTIVITY,
        )
        await self.change_presence(activity=activity)
        log.info("Bot is ready! Prefix: %s | Guilds: %d", BotConfig.PREFIX, len(self.guilds))

    async def on_command_error(self, ctx: commands.Context, error: Exception) -> None:
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing argument: `{error.param.name}`\nUsage: `{ctx.prefix}{ctx.command.qualified_name} {ctx.command.signature}`")
            return
        log.error("Command error in %s: %s", ctx.command, error, exc_info=error)
        await ctx.send(f"❌ An error occurred: {error}")


# ─── Main ─────────────────────────────────────────────────────────────────────

async def main() -> None:
    if not BotConfig.TOKEN:
        log.error("DISCORD_TOKEN is not set. Copy .env.example to .env and fill in your token.")
        sys.exit(1)

    bot = Botersson()
    async with bot:
        await bot.start(BotConfig.TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
