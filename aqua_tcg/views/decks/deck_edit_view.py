import discord
from discord.ui import View, Select, Button, Modal, TextInput
from discord import Interaction, SelectOption
from typing import TYPE_CHECKING

from aqua_tcg.models.user import CardDeck
from aqua_tcg.models.game_data import GameData

if TYPE_CHECKING:
    from aqua_tcg.models.game_data import GameData


class EditDeckView(View):
    def __init__(self, user_id: str, game_data: GameData, decks: list[CardDeck]) -> None:
        super().__init__(timeout=60)
        self.user_id = user_id
        self.game_data = game_data
        self.decks = decks

        self.add_item(EditDeckSelect(self))


class EditDeckSelect(Select):
    def __init__(self, parent_view: EditDeckView) -> None:
        self.parent_view = parent_view

        options = [
            SelectOption(label=f"{deck.name or f'Deck {i + 1}'}", value=str(i))
            for i, deck in enumerate(self.parent_view.decks)
        ]

        super().__init__(
            placeholder="Choose a deck to edit", options=options, min_values=1, max_values=1
        )

    async def callback(self, interaction: Interaction) -> None:
        index = int(self.values[0])
        view = SingleEditDeckView(
            deck_index=index, user_id=self.parent_view.user_id, game_data=self.parent_view.game_data
        )

        await interaction.response.edit_message(
            content=f"Editing Deck {index + 1}: **{self.parent_view.decks[index].name}**", view=view
        )


class SingleEditDeckView(View):
    def __init__(self, deck_index: int, user_id: str, game_data: GameData) -> None:
        super().__init__(timeout=120)
        self.deck_index = deck_index
        self.user_id = user_id
        self.game_data = game_data

        self.user = game_data.get_user(user_id)
        self.deck = self.user.decks[deck_index]

        self.character_selects: list[EditableCharacterSelect] = []

        for i in range(4):
            select = EditableCharacterSelect(
                index=i,
                parent_view=self,
                selected_char=self.deck.cards[i] if i < len(self.deck.cards) else None,
            )
            self.character_selects.append(select)
            self.add_item(select)

        self.add_item(ChangeDeckNameButton(parent_view=self))

    def get_selected_characters(self) -> list[str]:
        return [s.values[0] for s in self.character_selects if s.values]

    async def update_deck(self, interaction: Interaction) -> None:
        updated_chars = self.get_selected_characters()
        self.deck.cards = updated_chars
        self.game_data.save_users()

        await interaction.response.send_message(
            f"Deck updated: `{', '.join(updated_chars)}`", ephemeral=True
        )


class EditableCharacterSelect(Select):
    def __init__(
        self, index: int, parent_view: SingleEditDeckView, selected_char: str | None
    ) -> None:
        self.index = index
        self.parent_view = parent_view

        user_cards = parent_view.user.owned_cards
        selected = selected_char or (user_cards[0] if user_cards else "")

        options = [
            SelectOption(label=name, value=name, default=(name == selected)) for name in user_cards
        ]

        super().__init__(
            placeholder=f"Character {index + 1}", options=options, min_values=1, max_values=1
        )

    async def callback(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        # You could auto-update here if you want


class ChangeDeckNameButton(Button):
    def __init__(self, parent_view: SingleEditDeckView) -> None:
        super().__init__(label="Change Name", style=discord.ButtonStyle.secondary)
        self.parent_view = parent_view

    async def callback(self, interaction: Interaction) -> None:
        if interaction.user.id != int(self.parent_view.user_id):
            await interaction.response.send_message(
                "You can't rename someone else's deck.", ephemeral=True
            )
            return

        await interaction.response.send_modal(ChangeDeckNameModal(self.parent_view))


class ChangeDeckNameModal(Modal, title="Rename Your Deck"):
    def __init__(self, parent_view: SingleEditDeckView) -> None:
        super().__init__(timeout=60)
        self.parent_view = parent_view

        self.name_input = TextInput(
            label="New Deck Name", placeholder="Enter a new name", max_length=30
        )
        self.add_item(self.name_input)

    async def on_submit(self, interaction: Interaction) -> None:
        self.parent_view.deck.name = self.name_input.value
        self.parent_view.game_data.save_users()

        await interaction.response.send_message(
            f"Deck name changed to **{self.name_input.value}**", ephemeral=True
        )
