from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord.ui import Button, View

if TYPE_CHECKING:
    from durin_tcg.models.game import AIPlayer, Battle
    from durin_tcg.models.game_data import GameData


class BattleView(View):
    def __init__(
        self,
        player: discord.User | discord.Member,
        game: Battle,
        game_data: GameData,
        timeout: float = 60,
    ) -> None:
        super().__init__(timeout=timeout)
        self.player = player
        self.game = game
        self.game_data = game_data

        self.add_item(BattleActionButton("Basic Attack", "basic"))
        self.add_item(BattleActionButton("Skill", "skill"))
        self.add_item(BattleActionButton("Ultimate", "ultimate"))

    async def handle_action(self, interaction: discord.Interaction, action: str) -> None:
        await interaction.response.send_message(f"{self.player.display_name} used {action}!")


class PlayerBattleView(BattleView):
    def __init__(
        self,
        player1: discord.User | discord.Member,
        player2: discord.User,
        game: Battle,
        game_data: GameData,
    ) -> None:
        super().__init__(player1, game, game_data)
        self.opponent = player2


class AIBattleView(BattleView):
    def __init__(
        self, player: discord.User | discord.Member, ai: AIPlayer, game: Battle, game_data: GameData
    ) -> None:
        super().__init__(player, game, game_data)
        self.ai = ai


class BattleActionButton(Button):
    def __init__(self, label: str, action: str) -> None:
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.action = action

    async def callback(self, interaction: discord.Interaction) -> None:
        view: BattleView = self.view  # pyright: ignore[reportAssignmentType]
        await view.handle_action(interaction, self.action)
