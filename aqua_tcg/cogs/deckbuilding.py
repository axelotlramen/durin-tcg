from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from aqua_tcg.views.decks.deck_add_view import DeckAddView
from aqua_tcg.views.decks.deck_delete_view import DeleteDeckView

if TYPE_CHECKING:
    from aqua_tcg.bot import AquaBot
    from aqua_tcg.models.game_data import GameData


class Deckbuilding(commands.GroupCog, name="decks"):
    def __init__(self, bot: AquaBot, game_data: GameData) -> None:
        self.bot = bot
        self.game_data = game_data

    @app_commands.command(name="view", description="List all decks in a user's collection.")
    async def list_user_decks(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()

        uid = str(interaction.user.id)

        if uid not in self.game_data.users:
            self.game_data.add_user(uid)
            await interaction.followup.send(
                "You don't own any cards yet, but your Aqua TCG account has been created. Please use `/warp` or wait for `@axelotlramen` to implement this feature."
            )
            return

        user = self.game_data.get_user(uid)

        if not user.decks:
            await interaction.followup.send(
                "You haven't configured any decks yet. Please use `/decks add` or wait for `@axelotlramen` to implement this feature."
            )
            return

        embed = discord.Embed(
            title=f"{interaction.user.display_name}'s Decks", color=discord.Color.green()
        )

        for deck_num, deck in enumerate(user.decks):
            embed.add_field(name=f"Deck {deck_num + 1}", value=", ".join(deck.cards), inline=False)

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="add", description="List all available cards.")
    async def add_deck(self, interaction: discord.Interaction) -> None:
        uid = str(interaction.user.id)

        if uid not in self.game_data.users:
            self.game_data.add_user(uid)
            await interaction.response.send_message(
                "You don't own any cards yet, but your Aqua TCG account has been created. Please use `/warp` to get some cards."
            )
            return

        user = self.game_data.get_user(uid)

        if len(user.decks) >= 10:
            await interaction.response.send_message("You already have the maximum of 10 decks.")
            return

        user_cards = user.owned_cards

        if len(user_cards) < 4:
            await interaction.response.send_message(
                "You do not have enough cards (4+) to form a deck."
            )
            return

        view = DeckAddView(user_cards, uid, self.game_data)
        await interaction.response.send_message(
            "Select 4 unique characters for your new deck:", view=view
        )

    @app_commands.command(name="delete", description="Delete one of your decks.")
    async def delete_deck(self, interaction: discord.Interaction) -> None:
        uid = str(interaction.user.id)
        user = self.game_data.get_user(uid)

        if not user.decks:
            await interaction.response.send_message("You have no decks to delete.")
            return

        decks = [deck.cards for deck in user.decks]
        view = DeleteDeckView(uid, self.game_data, decks)

        await interaction.response.send_message(content="Select a deck to delete:", view=view)


async def setup(bot: AquaBot) -> None:
    await bot.add_cog(Deckbuilding(bot, bot.game_data))
