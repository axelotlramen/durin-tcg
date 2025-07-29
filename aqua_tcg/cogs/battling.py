from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from aqua_tcg.views.pvp_view import PvPGameView

from ..models.game import Battle, Character, Player
from ..utils.reading_cards import read_cards


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

        # Player 1
        hutao = Character(self.cards["Hu Tao"])
        sunday = Character(self.cards["Sunday"])
        danheng = Character(self.cards["Dan Heng"])
        hyacine = Character(self.cards["Hyacine"])

        # Player 2
        freminet = Character(self.cards["Freminet"])
        kazuha = Character(self.cards["Kaedehara Kazuha"])
        wrio = Character(self.cards["Wriothesley"])
        lycaon = Character(self.cards["Lycaon"])

        player1 = Player(deck=[hutao, sunday, danheng, hyacine], active_character=hutao)
        player2 = Player(deck=[freminet, kazuha, wrio, lycaon], active_character=freminet)

        game = Battle(player1, player2)
        view = PvPGameView(player1=interaction.user, player2=opponent, game=game)

        await interaction.response.send_message(
            content=f"{interaction.user.mention} vs {opponent.mention} - Battle begins!",
            embeds=[
                view.build_embed(interaction.user.display_name, player1),
                view.build_embed(opponent.display_name, player2),
            ],
            view=view,
        )

        view.message = await interaction.original_response()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Battling(bot))
