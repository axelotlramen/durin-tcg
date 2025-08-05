from __future__ import annotations

from typing import TYPE_CHECKING

from discord import Interaction, SelectOption
from discord.ui import Select, View

if TYPE_CHECKING:
    from aqua_tcg.models.game_data import GameData


class DeleteDeckView(View):
    def __init__(self, user_id: str, game_data: GameData, decks: list[list[str]]) -> None:
        super().__init__(timeout=60)
        self.user_id = user_id
        self.game_data = game_data
        self.decks = decks

        self.add_item(DeleteDeckSelect(self))


class DeleteDeckSelect(Select):
    def __init__(self, parent_view: DeleteDeckView) -> None:
        self.parent_view = parent_view

        options = [
            SelectOption(label=f"Deck {i + 1}", value=str(i)) for i in range(len(parent_view.decks))
        ]

        super().__init__(
            placeholder="Choose a deck to delete", options=options, min_values=1, max_values=1
        )

    async def callback(self, interaction: Interaction) -> None:
        index = int(self.values[0])
        user = self.parent_view.game_data.get_user(self.parent_view.user_id)
        deck = user.decks[index]

        card_list = ", ".join(deck.cards)
        user.decks.pop(index)
        self.parent_view.game_data.save_users()

        await interaction.response.edit_message(
            content=f"Deleted Deck {index + 1}:\n`{card_list}`", view=None
        )
        self.parent_view.stop()
