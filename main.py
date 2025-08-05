from __future__ import annotations

from typing import TYPE_CHECKING

import discord

from aqua_tcg.bot import AquaBot
from aqua_tcg.config import CONFIG

if TYPE_CHECKING:
    from discord.ext.commands import Context

bot = AquaBot()


@bot.command()
async def sync(context: Context) -> None:
    context.bot.tree.copy_global_to(guild=context.guild)
    synced_commands = await bot.tree.sync(guild=context.guild)
    embed = discord.Embed(
        description=f"{synced_commands} slash commands have been synchronized in this guild.",
        color=0xBEBEFE,
    )
    await context.send(embed=embed)


bot.run(CONFIG.discord_token)
