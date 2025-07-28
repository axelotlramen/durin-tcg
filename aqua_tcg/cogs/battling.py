from __future__ import annotations

from collections import defaultdict

import discord
from discord import app_commands
from discord.ext import commands

from ..enums import Game
from ..models.cards import Card
from ..models.game import Battle, Character, Player
from ..utils.reading_cards import read_cards


class Battling(commands.GroupCog, name="battle"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.cards = read_cards()

    @app_commands.command(name="cards", description="List all available cards.")
    async def list_cards(self, interaction: discord.Interaction) -> None:
        cards = self.cards
        if not cards:
            await interaction.response.send_message("No cards found.", ephemeral=True)
            return

        cards_by_game: dict[Game, list[Card]] = defaultdict(list)
        for card in cards.values():
            cards_by_game[card.game].append(card)

        embed = discord.Embed(
            title="All Available Cards",
            description="Here's a list of all cards and their elements:",
            color=discord.Color.blurple(),
        )

        for game in sorted(cards_by_game.keys()):
            card_lines = [
                f"• **{card.name}** — {card.element.value}"
                for card in sorted(cards_by_game[game], key=lambda c: c.name)
            ]
            embed.add_field(name=f"{game.value} Cards", value="\n".join(card_lines), inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="play_game", description="Simulate a game between Kazuha and Furina."
    )
    async def play_game(self, interaction: discord.Interaction) -> None:
        kazuha_card = self.cards["Kaedehara Kazuha"]
        furina_card = self.cards["Furina"]

        kazuha_character = Character(kazuha_card)
        furina_character = Character(furina_card)

        player1 = Player(deck=[kazuha_character], active_character=kazuha_character)
        player2 = Player(deck=[furina_character], active_character=furina_character)

        game = Battle(player1, player2)
        result = game.play_game()

        # Respond with battle log
        await interaction.response.send_message(f"**Battle Result:**\n```\n{result}\n```")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Battling(bot))
