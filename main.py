from __future__ import annotations

import os

import discord
from discord.ext.commands import Context
from dotenv import load_dotenv

from bot import AquaBot

load_dotenv()
TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID") or "")

if not TOKEN:
    raise ValueError("TOKEN is not set in the environment.")

bot = AquaBot()


@bot.event
async def on_ready():
    bot.logger.info(f"Bot is ready! Logged in as {bot.user}")


@bot.command()
async def sync(context: Context) -> None:
    context.bot.tree.copy_global_to(guild=context.guild)
    await bot.tree.sync(guild=context.guild)
    embed = discord.Embed(
        description="Slash commands have been synchronized in this guild.", color=0xBEBEFE
    )
    await context.send(embed=embed)


bot.run(TOKEN)
