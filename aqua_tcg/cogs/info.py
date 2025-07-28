from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands


class Info(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="help", description="Need help?")
    async def custom_help(self, interaction: discord.Interaction) -> None:
        embed = discord.Embed(
            title="Help?",
            description="This is not the help command. Maybe try a different one?",
            color=discord.Color.dark_gold(),
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    bot.remove_command("help")
    await bot.add_cog(Info(bot))
