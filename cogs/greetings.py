from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands


class Greetings(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="my_slash", description="Just a little slash command.")
    async def my_slash_command(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("This is a slash command in a cog!")

    @app_commands.command(name="ping", description="Replies with pong!")
    async def ping(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(f"Pong! The latency is {self.bot.latency}.")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Greetings(bot))
