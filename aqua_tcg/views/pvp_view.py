from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import Interaction
from discord.ui import Button, View

from aqua_tcg.enums import CardAbility

if TYPE_CHECKING:
    from aqua_tcg.models.game import Battle, Player


class PvPGameView(View):
    def __init__(
        self,
        player1: discord.User | discord.Member,
        player2: discord.User | discord.Member,
        game: Battle,
        message: discord.Message | None = None,
    ) -> None:
        super().__init__(timeout=300)
        self.discord_player1 = player1
        self.discord_player2 = player2
        self.game = game
        self.player1_turn = True  # Player 1 starts
        self.message = message

    async def on_timeout(self) -> None:
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True

        if self.message:
            await self.message.edit(content="Sorry, the battle timed out.", view=self)

    def current_user(self) -> discord.User | discord.Member:
        return self.discord_player1 if self.player1_turn else self.discord_player2

    def current_player(self) -> Player:
        return self.game.player1 if self.player1_turn else self.game.player2

    def enemy_player(self) -> Player:
        return self.game.player2 if self.player1_turn else self.game.player1

    def build_embed(self, title: str, player: Player) -> discord.Embed:
        active = player.active_character
        embed = discord.Embed(title=title)
        embed.add_field(name="Active Character", value=active.card.name, inline=False)
        embed.add_field(name="HP", value=str(active.current_hp), inline=True)
        return embed

    async def update_ui(self, interaction: discord.Interaction, message: discord.Message) -> None:
        user1_embed = self.build_embed(self.discord_player1.display_name, self.game.player1)
        user2_embed = self.build_embed(self.discord_player2.display_name, self.game.player2)

        await message.edit(
            content=f"It's {self.current_user().mention}'s turn!",
            embeds=[user1_embed, user2_embed],
            view=self,
        )

    async def take_turn(self, ability: CardAbility, interaction: Interaction) -> None:
        if interaction.user != self.current_user():
            await interaction.response.send_message("It's not your turn!", ephemeral=True)
            return

        self.current_player().use_ability(ability, self.enemy_player())

        if self.enemy_player().active_character.current_hp <= 0:
            for button in self.children:
                button.disabled = True
            await interaction.response.edit_message(
                content=f"{interaction.user.mention} wins!", view=self
            )
            return

        self.player1_turn = not self.player1_turn
        await self.update_ui(interaction, interaction.message)
        await interaction.response.defer()

    @discord.ui.button(label="Basic", style=discord.ButtonStyle.primary)
    async def basic_button(self, interaction: Interaction, _button: Button) -> None:
        await self.take_turn(CardAbility.BASIC, interaction)

    @discord.ui.button(label="Skill", style=discord.ButtonStyle.success)
    async def skill_button(self, interaction: Interaction, _button: Button) -> None:
        await self.take_turn(CardAbility.SKILL, interaction)

    @discord.ui.button(label="Ultimate", style=discord.ButtonStyle.danger)
    async def ultimate_button(self, interaction: Interaction, _button: Button) -> None:
        await self.take_turn(CardAbility.ULTIMATE, interaction)
