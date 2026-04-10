"""AI cog – LLM-powered commands via Ollama."""

from __future__ import annotations

import discord
from discord.ext import commands

from bot.services import llm
from bot.utils.helpers import truncate


class AICog(commands.Cog, name="AI"):
    """Commands powered by the local Ollama LLM."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # ── /ask ──────────────────────────────────────────────────────────────────

    @commands.hybrid_command(name="ask", description="Ask the AI a research question.")
    async def ask(self, ctx: commands.Context, *, question: str) -> None:
        """Ask the local LLM a question."""
        await ctx.defer()
        answer = await llm.async_answer(question, "")
        embed = discord.Embed(
            title="🤖 AI Answer",
            description=truncate(answer, 2000),
            color=discord.Color.gold(),
        )
        embed.set_footer(text=f"Question: {truncate(question, 100)}")
        await ctx.send(embed=embed)

    # ── /summarize ────────────────────────────────────────────────────────────

    @commands.hybrid_command(name="summarize", description="Summarize text using AI.")
    async def summarize(self, ctx: commands.Context, *, text: str) -> None:
        """Summarize a block of text using the local LLM."""
        await ctx.defer()
        summary = await llm.async_summarize(text)
        embed = discord.Embed(
            title="📝 Summary",
            description=truncate(summary, 2000),
            color=discord.Color.teal(),
        )
        await ctx.send(embed=embed)

    # ── /models ───────────────────────────────────────────────────────────────

    @commands.hybrid_command(name="models", description="List available Ollama AI models.")
    async def models(self, ctx: commands.Context) -> None:
        """Show locally available Ollama models."""
        model_list = llm.list_ollama_models()
        if not model_list:
            await ctx.send(
                "⚠️ No Ollama models found (or Ollama is not running).\n"
                "Start with `ollama serve` and pull a model: `ollama pull llama3.2`"
            )
            return
        embed = discord.Embed(
            title="🧠 Available Ollama Models",
            description="\n".join(f"• `{m}`" for m in model_list),
            color=discord.Color.blurple(),
        )
        await ctx.send(embed=embed)

    # ── /classify ─────────────────────────────────────────────────────────────

    @commands.hybrid_command(name="classify", description="Classify text into research themes using AI.")
    async def classify(self, ctx: commands.Context, topic: str, *, text: str) -> None:
        """Use Ollama to classify text into macro/meso/micro research themes."""
        await ctx.defer()
        classification = await llm.async_classify(text, "", topic)

        if "error" in classification and "themes" not in classification:
            await ctx.send(f"❌ {classification.get('error', 'Classification failed')}")
            return

        themes = classification.get("themes", {})
        embed = discord.Embed(
            title=f"🗂️ Theme Classification – {truncate(topic, 60)}",
            color=discord.Color.green(),
        )
        embed.add_field(name="📋 Summary", value=truncate(classification.get("summary", "N/A"), 400), inline=False)
        embed.add_field(name="🔑 Key Concepts", value=", ".join(classification.get("key_concepts", [])) or "N/A", inline=False)
        embed.add_field(name="📊 Relevance", value=f"{classification.get('relevance_score', 0)}/100", inline=True)
        embed.add_field(name="🌐 Macro", value="\n".join(f"• {t}" for t in themes.get("macro", [])) or "N/A", inline=False)
        embed.add_field(name="🔶 Meso", value="\n".join(f"• {t}" for t in themes.get("meso", [])[:5]) or "N/A", inline=False)
        embed.add_field(name="🔹 Micro", value="\n".join(f"• {t}" for t in themes.get("micro", [])[:6]) or "N/A", inline=False)
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AICog(bot))
