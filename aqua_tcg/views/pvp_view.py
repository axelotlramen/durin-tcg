from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import Interaction
from discord.ui import Button, View

from aqua_tcg.enums import CardAbility
from aqua_tcg.models.game import Character

if TYPE_CHECKING:
    from aqua_tcg.models.game import Battle, Player


class ChallengeAcceptView(View):
    def __init__(
        self,
        challenger: discord.User | discord.Member,
        opponent: discord.User | discord.Member,
        cards: dict,
    ) -> None:
        super().__init__(timeout=15)
        self.challenger = challenger
        self.opponent = opponent
        self.cards = cards
        self.message: discord.Message | None = None
        self.challenge_accepted = False

    async def on_timeout(self) -> None:
        if not self.challenge_accepted and self.message:
            for child in self.children:
                child.disabled = True
            await self.message.edit(content="Challenge expired due to no response.", view=self)

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success)
    async def accept_button(
        self, interaction: discord.Interaction, _button: discord.ui.Button
    ) -> None:
        if interaction.user.id != self.opponent.id:
            await interaction.response.send_message(
                "You are NOT the challenged player.", ephemeral=True
            )
            return

        self.challenge_accepted = True
        for child in self.children:
            child.disabled = True

        await interaction.message.edit(view=self)

        # Build player decks
        p1_deck = [
            Character(self.cards[name]) for name in ["Hu Tao", "Sunday", "Dan Heng", "Hyacine"]
        ]
        p2_deck = [
            Character(self.cards[name])
            for name in ["Freminet", "Kaedehara Kazuha", "Wriothesley", "Lycaon"]
        ]

        player1 = Player(deck=p1_deck, active_character=p1_deck[0])
        player2 = Player(deck=p2_deck, active_character=p2_deck[0])
        game = Battle(player1, player2)

        view = PvPGameView(player1=self.challenger, player2=self.opponent, game=game)

        # Send the actual battle message
        battle_message = await interaction.channel.send(
            content=f"{self.challenger.mention} vs {self.opponent.mention} - Battle begins!",
            embeds=[
                view.build_embed(self.challenger.display_name, player1),
                view.build_embed(self.opponent.display_name, player2),
            ],
            view=view,
        )
        view.message = battle_message

        # Ephemeral team info for both players
        await interaction.response.send_message(
            content=f"Your team:\n{view.get_team_info_text(player2)}", ephemeral=True
        )
        await interaction.followup.send(
            content=f"Your team:\n{view.get_team_info_text(player1)}",
            ephemeral=True,
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.danger)
    async def decline_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.opponent.id:
            await interaction.response.send_message(
                "You're not the challenged player.", ephemeral=True
            )
            return

        for child in self.children:
            child.disabled = True
        await interaction.message.edit(
            content=f"{self.opponent.mention} declined the challenge from {self.challenger.mention}.",
            view=self,
        )
        await interaction.response.send_message("You declined the challenge.", ephemeral=True)


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

        self.add_item(SwitchCharacterButton())

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

    def get_team_info_text(self, player: Player) -> str:
        return "\n".join(
            f"{char.card.name} (HP: {char.current_hp})"
            + (" [Active]" if char == player.active_character else "")
            for char in player.deck
        )

    async def update_ui(
        self, interaction: discord.Interaction, message: discord.Message | None = None
    ) -> None:
        message = message or self.message
        channel = message.channel if message else interaction.channel

        if message:
            try:
                await message.delete()
            except discord.NotFound:
                pass

        user1_embed = self.build_embed(self.discord_player1.display_name, self.game.player1)
        user2_embed = self.build_embed(self.discord_player2.display_name, self.game.player2)

        new_message = await channel.send(
            content=f"It's {self.current_user().mention}'s turn!",
            embeds=[user1_embed, user2_embed],
            view=self,
        )

        self.message = new_message

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

        await interaction.response.defer()

        await self.update_ui(interaction, self.message)

        current_player = self.current_player()
        team_info = self.get_team_info_text(current_player)
        await interaction.followup.send(content=f"Your team: \n{team_info}", ephemeral=True)

    @discord.ui.button(label="Basic", style=discord.ButtonStyle.primary)
    async def basic_button(self, interaction: Interaction, _button: Button) -> None:
        await self.take_turn(CardAbility.BASIC, interaction)

    @discord.ui.button(label="Skill", style=discord.ButtonStyle.success)
    async def skill_button(self, interaction: Interaction, _button: Button) -> None:
        await self.take_turn(CardAbility.SKILL, interaction)

    @discord.ui.button(label="Ultimate", style=discord.ButtonStyle.danger)
    async def ultimate_button(self, interaction: Interaction, _button: Button) -> None:
        await self.take_turn(CardAbility.ULTIMATE, interaction)


class SwitchCharacterButton(discord.ui.Button):
    def __init__(self) -> None:
        super().__init__(label="Switch Character", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction) -> None:
        view: PvPGameView = self.view
        if interaction.user != view.current_user():
            await interaction.response.send_message("It's not your turn!", ephemeral=True)
            return

        character_select_view = CharacterSelectView(view)
        await interaction.response.send_message(
            content="Choose a character to switch to:", view=character_select_view, ephemeral=True
        )


class CharacterSelectView(discord.ui.View):
    def __init__(self, game_view: PvPGameView):
        super().__init__(timeout=30)
        self.game_view = game_view
        self.player = game_view.game.player1 if game_view.player1_turn else game_view.game.player2

        for i, char in enumerate(self.player.deck):
            if char != self.player.active_character:
                self.add_item(SingleCharacterButton(index=i, char_name=char.card.name))


class SingleCharacterButton(discord.ui.Button):
    def __init__(self, index: int, char_name: str):
        super().__init__(label=char_name, style=discord.ButtonStyle.primary)
        self.index = index

    async def callback(self, interaction: discord.Interaction):
        game_view = self.view.game_view
        player = self.view.player

        if interaction.user != game_view.current_user():
            await interaction.response.send_message("It's not your turn!", ephemeral=True)
            return

        player.switch_character(self.index)

        await interaction.response.send_message(
            f"Switched to {player.active_character.card.name}!", ephemeral=True
        )

        await game_view.update_ui(interaction)
