from __future__ import annotations

from typing import TYPE_CHECKING

from durin_tcg.constants import CARD_BASIC_ATTACK, CARD_SKILL_ATTACK, CARD_ULTIMATE_ATTACK
from durin_tcg.enums import Game
from durin_tcg.exceptions import InvalidAbilityUseError

if TYPE_CHECKING:
    from collections.abc import Callable

    from durin_tcg.enums import CardElement
    from durin_tcg.models.game import Character, Player


class Ability:
    def __init__(
        self,
        name: str,
        desc: str,
        element: CardElement,
        damage_number: int,
        target: str = "enemy",
        use_func: Callable[[list[Character], Player], None] | None = None,
    ) -> None:
        self.name = name
        self.desc = desc
        self.element = element
        self.damage_number = damage_number
        self.target = target

        if use_func is not None:
            self._use_func = use_func
        else:
            self._use_func = self.default_use

    def default_use(self, allies: list[Character], enemy: Player) -> None:
        if self.target == "enemy":
            enemy_active = enemy.active_character
            damage = self.damage_number

            if enemy_active.current_shield > 0:
                if damage <= enemy_active.current_shield:
                    enemy_active.current_shield -= damage
                    damage = 0
                else:
                    damage -= enemy_active.current_shield
                    enemy_active.current_shield = 0

            enemy_active.current_hp = max(enemy_active.current_hp - damage, 0)
            return

        live_allies = [a for a in allies if a.final_hp > 0]
        if not live_allies:
            msg = f"No valid ally targets for skill: {self.name}"
            raise InvalidAbilityUseError(msg)

        msg = "Buffs/Healing not implemented yet."
        raise NotImplementedError(msg)

    def use(self, allies: list[Character], enemy: Player) -> None:
        return self._use_func(allies, enemy)


class Card:
    # Set up the card object
    def __init__(self, name: str, desc: str, game: Game, element: CardElement) -> None:
        self.name = name
        self.desc = desc
        self.game = game
        self.element = element

        self.basic = Ability(
            name=f"{self.name} Basic",
            desc=f"{self.name} strikes an enemy.",
            element=self.element,
            damage_number=CARD_BASIC_ATTACK,
        )
        self.skill = Ability(
            name=f"{self.name} Skill",
            desc=f"{self.name} uses their unique ability.",
            element=self.element,
            damage_number=CARD_SKILL_ATTACK,
        )
        self.ultimate = Ability(
            name=f"{self.name} Ultimate",
            desc=f"{self.name} unleashes a devastating ultimate attack.",
            element=self.element,
            damage_number=CARD_ULTIMATE_ATTACK,
        )

    def __repr__(self) -> str:
        return "**" + self.name + "* : " + self.desc

    def __str__(self) -> str:
        return "**" + self.name + "* : " + self.desc


class GenshinCard(Card):
    def __init__(self, name: str, desc: str, element: CardElement) -> None:
        super().__init__(name, desc, Game.GENSHIN, element)


class HSRCard(Card):
    def __init__(self, name: str, desc: str, element: CardElement) -> None:
        super().__init__(name, desc, Game.HSR, element)


class ZZZCard(Card):
    def __init__(self, name: str, desc: str, element: CardElement) -> None:
        super().__init__(name, desc, Game.ZZZ, element)
