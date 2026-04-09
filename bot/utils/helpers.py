"""Helper utilities for the Botersson Discord bot."""

from __future__ import annotations

import discord


def truncate(text: str, max_len: int = 200) -> str:
    """Truncate a string to max_len characters, appending … if needed."""
    if not text:
        return ""
    text = str(text)
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


def paginate_embed(
    title: str,
    items: list[str],
    color: discord.Color = discord.Color.blue(),
    max_items: int = 10,
) -> discord.Embed:
    """Create a simple embed with a list of items."""
    embed = discord.Embed(title=title, color=color)
    displayed = items[:max_items]
    for item in displayed:
        embed.add_field(name="\u200b", value=item, inline=False)
    if len(items) > max_items:
        embed.set_footer(text=f"Showing {max_items} of {len(items)} items")
    return embed


def success_embed(title: str, description: str = "") -> discord.Embed:
    return discord.Embed(title=f"✅ {title}", description=description, color=discord.Color.green())


def error_embed(title: str, description: str = "") -> discord.Embed:
    return discord.Embed(title=f"❌ {title}", description=description, color=discord.Color.red())


def info_embed(title: str, description: str = "") -> discord.Embed:
    return discord.Embed(title=f"ℹ️ {title}", description=description, color=discord.Color.blue())
