"""Patents cog – patent and academic article search commands."""

from __future__ import annotations

from urllib.parse import urlparse

import discord
from discord.ext import commands

from bot.services import excel_manager, llm, patent_search, scraper
from bot.utils.helpers import truncate


class PatentsCog(commands.Cog, name="Patents & Articles"):
    """Commands for finding and analysing patents and academic papers."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # ── /patent ───────────────────────────────────────────────────────────────

    @commands.hybrid_command(name="patent", description="Search Google Patents for patents.")
    async def patent(self, ctx: commands.Context, *, query: str) -> None:
        """Search Google Patents."""
        await ctx.defer()
        results = await patent_search.async_search_patents(query)

        if not results or "error" in results[0]:
            err = results[0].get("error", "No results") if results else "No results"
            await ctx.send(f"❌ Patent search error: {err}")
            return

        embed = discord.Embed(
            title=f"⚗️ Patents: {truncate(query, 100)}",
            color=discord.Color.purple(),
        )
        for i, p in enumerate(results[:6], 1):
            embed.add_field(
                name=f"{i}. {truncate(p.get('title', 'No title'), 80)}",
                value=(
                    f"**ID:** {p.get('patent_id', 'N/A')}\n"
                    f"**Assignee:** {truncate(p.get('assignee', 'N/A'), 60)}\n"
                    f"**Date:** {p.get('date', 'N/A')}\n"
                    f"[🔗 View Patent]({p.get('url', '')})"
                ),
                inline=False,
            )
        embed.set_footer(text="Use /analyze_patent <url> to analyse a specific patent with AI")
        await ctx.send(embed=embed)

    # ── /article ──────────────────────────────────────────────────────────────

    @commands.hybrid_command(name="article", description="Search Semantic Scholar for academic articles.")
    async def article(self, ctx: commands.Context, *, query: str) -> None:
        """Search academic articles via Semantic Scholar."""
        await ctx.defer()
        results = await patent_search.async_search_articles(query)

        if not results or "error" in results[0]:
            err = results[0].get("error", "No results") if results else "No results"
            await ctx.send(f"❌ Article search error: {err}")
            return

        embed = discord.Embed(
            title=f"📚 Articles: {truncate(query, 100)}",
            color=discord.Color.red(),
        )
        for i, a in enumerate(results[:6], 1):
            embed.add_field(
                name=f"{i}. {truncate(a.get('title', 'No title'), 80)}",
                value=(
                    f"**Authors:** {truncate(a.get('authors', 'N/A'), 80)}\n"
                    f"**Year:** {a.get('year', 'N/A')}\n"
                    f"**DOI:** {a.get('doi', 'N/A')}\n"
                    f"{('[🔗 Link](' + a.get('url') + ')') if a.get('url') else ''}"
                ),
                inline=False,
            )
        embed.set_footer(text="Use /analyze_article <url> to analyse with AI")
        await ctx.send(embed=embed)

    # ── /arxiv ────────────────────────────────────────────────────────────────

    @commands.hybrid_command(name="arxiv", description="Search arXiv preprints.")
    async def arxiv(self, ctx: commands.Context, *, query: str) -> None:
        """Search arXiv preprints."""
        await ctx.defer()
        results = await patent_search.async_search_arxiv(query)

        if not results or "error" in results[0]:
            err = results[0].get("error", "No results") if results else "No results"
            await ctx.send(f"❌ arXiv search error: {err}")
            return

        embed = discord.Embed(
            title=f"📄 arXiv: {truncate(query, 100)}",
            color=discord.Color.from_rgb(180, 0, 0),
        )
        for i, a in enumerate(results[:6], 1):
            embed.add_field(
                name=f"{i}. {truncate(a.get('title', 'No title'), 80)}",
                value=(
                    f"**Authors:** {truncate(a.get('authors', 'N/A'), 80)}\n"
                    f"**Published:** {a.get('published', 'N/A')}\n"
                    f"{('[🔗 Link](' + a.get('url') + ')') if a.get('url') else ''}"
                ),
                inline=False,
            )
        await ctx.send(embed=embed)

    # ── /analyze_patent ───────────────────────────────────────────────────────

    @commands.hybrid_command(name="analyze_patent", description="Scrape and analyse a patent URL with AI.")
    async def analyze_patent(self, ctx: commands.Context, url: str, *, topic: str = "research") -> None:
        """Scrape a patent page and classify its content using Ollama."""
        await ctx.defer()

        # Scrape the patent – use netloc-based check to avoid substring confusion
        _parsed = urlparse(url)
        _is_google_patents = _parsed.netloc in ("patents.google.com", "www.patents.google.com")

        if _is_google_patents:
            result = await patent_search.async_scrape_patent(url)
            text = f"{result.get('abstract', '')} {result.get('claims', '')} {result.get('description', '')}"
            title = result.get("title", "Patent")
        else:
            result = await scraper.async_scrape_url(url)
            text = result.get("text", "")
            title = result.get("title", "Patent")

        if not text.strip():
            await ctx.send("❌ Could not extract text from the patent URL.")
            return

        await ctx.send(f"🤖 Classifying **{truncate(title, 100)}** with AI…")

        classification = await llm.async_classify(text, title, topic)

        if "error" in classification and "themes" not in classification:
            await ctx.send(f"❌ {classification['error']}")
            return

        themes = classification.get("themes", {})
        embed = discord.Embed(
            title=f"⚗️ Patent Analysis: {truncate(title, 100)}",
            url=url,
            color=discord.Color.purple(),
        )
        embed.add_field(name="📋 Summary", value=truncate(classification.get("summary", "N/A"), 500), inline=False)
        embed.add_field(name="🔑 Key Concepts", value=", ".join(classification.get("key_concepts", [])) or "N/A", inline=False)
        embed.add_field(name="📊 Relevance", value=f"{classification.get('relevance_score', 0)}/100", inline=True)
        embed.add_field(name="🌐 Macro Themes", value="\n".join(f"• {t}" for t in themes.get("macro", [])) or "N/A", inline=False)
        embed.add_field(name="🔶 Meso Themes", value="\n".join(f"• {t}" for t in themes.get("meso", [])[:5]) or "N/A", inline=False)
        embed.add_field(name="🔹 Micro Themes", value="\n".join(f"• {t}" for t in themes.get("micro", [])[:6]) or "N/A", inline=False)

        # Save to Excel
        patent_data = {
            "title": title,
            "url": url,
            "abstract": result.get("abstract", text[:500]),
            "patent_id": "",
            "assignee": "",
            "inventor": "",
            "date": "",
        }
        row_id = excel_manager.save_patent(patent_data, classification)
        embed.set_footer(text=f"✅ Saved to Excel (Patents row #{row_id})")
        await ctx.send(embed=embed)

    # ── /analyze_article ──────────────────────────────────────────────────────

    @commands.hybrid_command(name="analyze_article", description="Scrape and analyse an article URL with AI.")
    async def analyze_article(self, ctx: commands.Context, url: str, *, topic: str = "research") -> None:
        """Scrape an article page and classify its content using Ollama."""
        await ctx.defer()

        result = await scraper.async_scrape_url(url)
        if not result.get("success"):
            await ctx.send(f"❌ Could not scrape the URL: {result.get('error', 'Unknown error')}")
            return

        text = result.get("text", "")
        title = result.get("title", "Article")

        await ctx.send(f"🤖 Classifying **{truncate(title, 100)}** with AI…")
        classification = await llm.async_classify(text, title, topic)

        if "error" in classification and "themes" not in classification:
            await ctx.send(f"❌ {classification['error']}")
            return

        themes = classification.get("themes", {})
        embed = discord.Embed(
            title=f"📚 Article Analysis: {truncate(title, 100)}",
            url=url,
            color=discord.Color.red(),
        )
        embed.add_field(name="📋 Summary", value=truncate(classification.get("summary", "N/A"), 500), inline=False)
        embed.add_field(name="🔑 Key Concepts", value=", ".join(classification.get("key_concepts", [])) or "N/A", inline=False)
        embed.add_field(name="📊 Relevance", value=f"{classification.get('relevance_score', 0)}/100", inline=True)
        embed.add_field(name="🌐 Macro Themes", value="\n".join(f"• {t}" for t in themes.get("macro", [])) or "N/A", inline=False)
        embed.add_field(name="🔶 Meso Themes", value="\n".join(f"• {t}" for t in themes.get("meso", [])[:5]) or "N/A", inline=False)
        embed.add_field(name="🔹 Micro Themes", value="\n".join(f"• {t}" for t in themes.get("micro", [])[:6]) or "N/A", inline=False)

        article_data = {
            "title": title,
            "url": url,
            "abstract": result.get("meta_description", text[:500]),
            "authors": "",
            "year": "",
            "doi": "",
        }
        row_id = excel_manager.save_article(article_data, classification)
        embed.set_footer(text=f"✅ Saved to Excel (Articles row #{row_id})")
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PatentsCog(bot))
