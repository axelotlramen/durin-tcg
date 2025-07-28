from __future__ import annotations

import os
from typing import TYPE_CHECKING

import discord
from dotenv import load_dotenv

from aqua_tcg.bot import AquaBot

if TYPE_CHECKING:
    from discord.ext.commands import Context

load_dotenv()
TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID") or "")

if not TOKEN:
    msg = "TOKEN is not set in the environment."
    raise ValueError(msg)

bot = AquaBot()


@bot.event
async def on_ready() -> None:
    bot.logger.info("Bot is ready! Logged in as %s", bot.user)


@bot.command()
async def sync(context: Context) -> None:
    context.bot.tree.copy_global_to(guild=context.guild)
    await bot.tree.sync(guild=context.guild)
    embed = discord.Embed(
        description="Slash commands have been synchronized in this guild.", color=0xBEBEFE
    )
    await context.send(embed=embed)


bot.run(TOKEN)
