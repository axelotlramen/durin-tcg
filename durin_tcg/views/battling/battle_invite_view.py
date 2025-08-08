from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

import discord
from discord import Embed, Interaction
from discord.ui import Button, View

from durin_tcg.views.battling.switch_deck_view import SwitchDeckView

if TYPE_CHECKING:
    from durin_tcg.commands.battling import BattleCommand
    from durin_tcg.models.user import CardDeck


class BattleInviteView(View):
    def __init__(
        self,
        user: discord.User | discord.Member,
        battle_command: BattleCommand,
        timeout: float = 60,
    ) -> None:
        super().__init__(timeout=timeout)

        self.user = user
        self.battle_command = battle_command

        self.selected_deck_index = self._get_selected_deck_index()
        self.selected_deck = self._get_selected_deck()

        self.add_item(SwitchDeckButton())
        self.add_item(SendInviteButton())

    def _get_selected_deck_index(self) -> int:
        return self.battle_command.game_data.get_user(str(self.user.id)).active_deck_index

    def _get_selected_deck(self) -> CardDeck:
        return self.battle_command.game_data.get_user(str(self.user.id)).decks[
            self.selected_deck_index
        ]

    async def send_summary(self, interaction: Interaction) -> None:
        opponent_name = (
            self.battle_command.opponent
            if isinstance(self.battle_command.opponent, str)
            else self.battle_command.opponent.display_name
        )

        card_list = "\n".join(f"• {card}" for card in self.selected_deck.cards)

        embed = Embed(
            title="Battle Invitation",
            description=(f"**Opponent:** {opponent_name}\n**Your Deck:**\n{card_list}"),
            color=discord.Color.blurple(),
        )

        try:
            await interaction.response.send_message(embed=embed, view=self)
        except discord.InteractionResponded:
            await interaction.followup.send(embed=embed, view=self)


class SwitchDeckButton(Button):
    def __init__(self) -> None:
        super().__init__(label="Switch Deck", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction) -> None:
        view: BattleInviteView = self.view  # pyright: ignore[reportAssignmentType]

        switch_view = SwitchDeckView(
            user=view.user,
            selected_deck_index=view.selected_deck_index,
            selected_deck=view.selected_deck,
            battle_command=view.battle_command,
            on_confirm=view.send_summary,
        )

        await switch_view.send_switch_prompt(interaction)


class SendInviteButton(Button):
    def __init__(self) -> None:
        super().__init__(label="Send Invitation", style=discord.ButtonStyle.success)

    async def callback(self, interaction: discord.Interaction) -> None:
        view: BattleInviteView = self.view  # pyright: ignore[reportAssignmentType]
        if view.battle_command.opponent == "AI":
            new_view = await view.battle_command.run_ai()
        else:
            new_view = await view.battle_command.run_player()

        with contextlib.suppress(discord.NotFound):
            await interaction.message.edit(  # pyright: ignore[reportOptionalMemberAccess]
                content="Battle invitation successfully sent!", view=None, embed=None
            )

        try:
            await interaction.response.send_message(content="Battle begins!", view=new_view)
        except discord.InteractionResponded:
            await interaction.followup.send(content="Battle begins!", view=new_view)
