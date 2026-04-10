"""Search cog – internet search commands for the Discord bot."""

from __future__ import annotations

import discord
from discord.ext import commands

from bot.services import search_engine, scraper
from bot.utils.helpers import paginate_embed, truncate


class SearchCog(commands.Cog, name="Search"):
    """Commands for searching the internet."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # ── /search ───────────────────────────────────────────────────────────────

    @commands.hybrid_command(name="search", description="Search with optional scope filters.")
    async def search(self, ctx: commands.Context, scope: str = "web", *, query: str) -> None:
        """Search the web using DuckDuckGo with optional scopes."""
        await ctx.defer()
        results = await search_engine.async_search_web_scoped(query, scope)

        if not results:
            await ctx.send("❌ No results found.")
            return

        if results and "error" in results[0]:
            await ctx.send(f"❌ Search error: {results[0]['error']}")
            return

        embed = discord.Embed(
            title=f"🔍 Search ({truncate(scope, 20)}): {truncate(query, 100)}",
            color=discord.Color.blue(),
        )
        for i, r in enumerate(results[:8], 1):
            embed.add_field(
                name=f"{i}. {truncate(r.get('title', 'No title'), 80)}",
                value=f"{truncate(r.get('snippet', ''), 150)}\n[🔗 Link]({r.get('url', '')})",
                inline=False,
            )
        await ctx.send(embed=embed)

    # ── /news ─────────────────────────────────────────────────────────────────

    @commands.hybrid_command(name="news", description="Search recent news about a topic.")
    async def news(self, ctx: commands.Context, *, query: str) -> None:
        """Search recent news via DuckDuckGo."""
        await ctx.defer()
        results = await search_engine.async_search_news(query)

        if not results or "error" in results[0]:
            await ctx.send("❌ No news results found.")
            return

        embed = discord.Embed(
            title=f"📰 News: {truncate(query, 100)}",
            color=discord.Color.green(),
        )
        for i, r in enumerate(results[:8], 1):
            date = r.get("date", "")
            source = r.get("source", "")
            header = f"{i}. {truncate(r.get('title', 'No title'), 80)}"
            if source or date:
                header += f" | {source} {date}"
            embed.add_field(
                name=header,
                value=f"{truncate(r.get('snippet', ''), 150)}\n[🔗 Link]({r.get('url', '')})",
                inline=False,
            )
        await ctx.send(embed=embed)

    # ── /scrape ───────────────────────────────────────────────────────────────

    @commands.hybrid_command(name="scrape", description="Extract text content from a URL.")
    async def scrape(self, ctx: commands.Context, url: str) -> None:
        """Scrape a webpage and show its title and text excerpt."""
        await ctx.defer()
        result = await scraper.async_scrape_url(url)

        if not result.get("success"):
            await ctx.send(f"❌ Could not scrape `{url}`\nError: {result.get('error', 'Unknown error')}")
            return

        embed = discord.Embed(
            title=f"🕷️ {truncate(result.get('title', 'No title'), 200)}",
            url=url,
            description=truncate(result.get("text", ""), 800),
            color=discord.Color.orange(),
        )
        meta = result.get("meta_description", "")
        if meta:
            embed.add_field(name="📝 Description", value=truncate(meta, 200), inline=False)
        embed.add_field(name="🔗 Links found", value=str(len(result.get("links", []))), inline=True)
        embed.set_footer(text="Use /analyze <url> to classify this content with AI")
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SearchCog(bot))
