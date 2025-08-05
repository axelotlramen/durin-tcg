from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from aqua_tcg.bot import AquaBot

if TYPE_CHECKING:
    from aqua_tcg.bot import AquaBot


class Info(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="ping", description="Replies with pong!")
    async def ping(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(f"Pong! The latency is {self.bot.latency}.")

    @app_commands.command(name="help", description="Need help?")
    async def custom_help(self, interaction: discord.Interaction) -> None:
        embed = discord.Embed(
            title="Help?",
            description="This is not the help command. Maybe try a different one?",
            color=discord.Color.dark_gold(),
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: AquaBot) -> None:
    bot.remove_command("help")
    await bot.add_cog(Info(bot))
