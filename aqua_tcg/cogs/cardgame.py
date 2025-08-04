from __future__ import annotations

from collections import defaultdict

import discord
from discord import app_commands
from discord.ext import commands

from aqua_tcg.models.user import TCGUser
from aqua_tcg.utils.reading_users import load_all_users, save_all_users

from aqua_tcg.enums import Game
from aqua_tcg.models.cards import Card
from aqua_tcg.models.game import Battle, Character, Player
from aqua_tcg.utils.reading_cards import read_cards


class CardGame(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.cards = read_cards()
        self.users = load_all_users()

    @app_commands.command(name="my_cards", description="List all cards in a user's collection.")
    async def list_user_cards(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()

        uid = str(interaction.user.id)

        if uid not in self.users:
            self.users[uid] = TCGUser()
            save_all_users(self.users)
            await interaction.followup.send(
                "You don't own any cards yet, but your Aqua TCG account has been created. Please use `/warp` or wait for `@axelotlramen` to implement this feature."
            )
            return

        user = self.users[uid]

        if not user.owned_cards:
            await interaction.followup.send(
                "You don't own any cards yet. Please use `/warp` or wait for `@axelotlramen` to implement this feature."
            )
            return

    @app_commands.command(name="all_cards", description="List all available cards.")
    async def list_all_cards(self, interaction: discord.Interaction) -> None:
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
    await bot.add_cog(CardGame(bot))
