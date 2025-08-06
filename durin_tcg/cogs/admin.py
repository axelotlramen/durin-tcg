from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord.ext import commands
from discord.ext.commands import Context

from durin_tcg.bot import DurinBot

if TYPE_CHECKING:
    from durin_tcg.bot import DurinBot


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command()
    async def sync(self, context: Context) -> None:
        context.bot.tree.copy_global_to(guild=context.guild)
        synced_commands = await self.bot.tree.sync(guild=context.guild)
        embed = discord.Embed(
            description=f"{len(synced_commands)} slash commands have been synchronized in this guild.",
            color=0xBEBEFE,
        )
        await context.send(embed=embed)


async def setup(bot: DurinBot) -> None:
    bot.remove_command("help")
    await bot.add_cog(Admin(bot))
