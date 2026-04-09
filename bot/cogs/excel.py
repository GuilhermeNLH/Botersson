"""Excel cog – commands to interact with the research Excel database."""

from __future__ import annotations

import io

import discord
from discord.ext import commands

from bot.services import excel_manager
from bot.utils.helpers import truncate


class ExcelCog(commands.Cog, name="Excel"):
    """Commands for the Excel research database."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # ── /db_summary ───────────────────────────────────────────────────────────

    @commands.hybrid_command(name="db_summary", description="Show a summary of the research database.")
    async def db_summary(self, ctx: commands.Context) -> None:
        """Display row counts for each sheet in the Excel database."""
        summary = excel_manager.get_all_sheets_summary()
        embed = discord.Embed(
            title="📊 Research Database Summary",
            color=discord.Color.blue(),
        )
        total = 0
        for sheet_name, count in summary.items():
            embed.add_field(name=sheet_name, value=str(count), inline=True)
            total += count
        embed.set_footer(text=f"Total records: {total} | Use /chart to generate a visual")
        await ctx.send(embed=embed)

    # ── /chart ────────────────────────────────────────────────────────────────

    @commands.hybrid_command(name="chart", description="Generate a chart of the research database.")
    async def chart(
        self,
        ctx: commands.Context,
        chart_type: str = "bar",
        *,
        topic: str = "",
    ) -> None:
        """
        Generate a chart showing database contents.
        chart_type: bar | pie | line
        """
        await ctx.defer()
        buf = excel_manager.generate_chart(chart_type=chart_type, topic=topic)
        file = discord.File(fp=buf, filename="chart.png")
        embed = discord.Embed(
            title=f"📈 Research Chart ({chart_type}){' – ' + topic if topic else ''}",
            color=discord.Color.blue(),
        )
        embed.set_image(url="attachment://chart.png")
        await ctx.send(embed=embed, file=file)

    # ── /theme_chart ──────────────────────────────────────────────────────────

    @commands.hybrid_command(name="theme_chart", description="Chart the macro/meso/micro theme distribution.")
    async def theme_chart(self, ctx: commands.Context, *, topic: str = "") -> None:
        """Generate a bar chart of themes distribution."""
        await ctx.defer()
        buf = excel_manager.generate_themes_chart(topic=topic)
        file = discord.File(fp=buf, filename="themes.png")
        embed = discord.Embed(
            title=f"🗂️ Themes Distribution{' – ' + topic if topic else ''}",
            color=discord.Color.green(),
        )
        embed.set_image(url="attachment://themes.png")
        await ctx.send(embed=embed, file=file)

    # ── /list_sheet ───────────────────────────────────────────────────────────

    @commands.hybrid_command(name="list_sheet", description="List entries from a database sheet.")
    async def list_sheet(
        self,
        ctx: commands.Context,
        sheet: str = "Articles",
        limit: int = 5,
    ) -> None:
        """
        Show recent entries from a sheet.
        sheet: Articles | Patents | Macro Themes | Meso Themes | Micro Themes | Search Results
        """
        valid = ["Articles", "Patents", "Macro Themes", "Meso Themes", "Micro Themes", "Search Results"]
        if sheet not in valid:
            await ctx.send(f"❌ Invalid sheet. Choose from: {', '.join(valid)}")
            return

        rows = excel_manager.get_sheet_data(sheet)
        if not rows:
            await ctx.send(f"📂 **{sheet}** is empty.")
            return

        embed = discord.Embed(
            title=f"📋 {sheet} (last {min(limit, len(rows))} of {len(rows)})",
            color=discord.Color.teal(),
        )
        for row in rows[-limit:]:
            title_key = "Title" if "Title" in row else "Theme"
            title = truncate(str(row.get(title_key, "N/A")), 80)
            details: list[str] = []
            for key in ["Authors", "Year", "Patent ID", "Assignee", "Date", "Query", "Source Type"]:
                if key in row and row[key]:
                    details.append(f"**{key}:** {truncate(str(row[key]), 60)}")
            embed.add_field(name=title, value="\n".join(details) or "No details", inline=False)
        embed.set_footer(text="Use the web GUI for full table management")
        await ctx.send(embed=embed)

    # ── /add_theme ────────────────────────────────────────────────────────────

    @commands.hybrid_command(name="add_theme", description="Add a macro/meso/micro theme to the database.")
    async def add_theme(
        self,
        ctx: commands.Context,
        theme_type: str,
        theme: str,
        parent: str = "",
        *,
        description: str = "",
    ) -> None:
        """
        Add a theme to the database.
        theme_type: macro | meso | micro
        """
        valid_types = ["macro", "meso", "micro"]
        if theme_type.lower() not in valid_types:
            await ctx.send(f"❌ theme_type must be one of: {', '.join(valid_types)}")
            return

        row_id = excel_manager.save_theme(theme_type, theme, parent, description)
        await ctx.send(
            f"✅ Added **{theme_type.upper()}** theme: `{theme}` (ID: {row_id})"
        )

    # ── /export_excel ─────────────────────────────────────────────────────────

    @commands.hybrid_command(name="export_excel", description="Download the research Excel file.")
    async def export_excel(self, ctx: commands.Context) -> None:
        """Send the Excel file as a Discord attachment."""
        await ctx.defer()
        path = excel_manager.workbook_path()
        if not path.exists():
            excel_manager.ensure_workbook()

        file = discord.File(fp=str(path), filename=path.name)
        await ctx.send(
            content=f"📥 Here is your research database ({path.stat().st_size // 1024} KB):",
            file=file,
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ExcelCog(bot))
