from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from aqua_tcg.views.pvp_view import ChallengeAcceptView, PvPGameView

from aqua_tcg.models.game import Battle, Character, Player
from aqua_tcg.utils.reading_cards import read_cards


class Battling(commands.GroupCog, name="battle"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.cards = read_cards()

    @app_commands.command(name="player", description="Challenge another player")
    @app_commands.describe(opponent="The user you want to challenge.")
    async def challange_player(
        self, interaction: discord.Interaction, opponent: discord.User
    ) -> None:
        if opponent.id == interaction.user.id:
            await interaction.response.send_message("You can't challenge yourself.", ephemeral=True)
            return

        embed = discord.Embed(
            title="Battle Challenge",
            description=f"{interaction.user.mention} has challenged {opponent.mention} to a duel!",
            color=discord.Color.orange(),
        )

        view = ChallengeAcceptView(challenger=interaction.user, opponent=opponent, cards=self.cards)

        await interaction.response.send_message(embed=embed, view=view)
        view.message = await interaction.original_response()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Battling(bot))
