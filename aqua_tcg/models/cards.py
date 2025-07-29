from __future__ import annotations

from typing import TYPE_CHECKING

from aqua_tcg.constants import CARD_BASIC_ATTACK, CARD_SKILL_ATTACK, CARD_ULTIMATE_ATTACK
from aqua_tcg.enums import Game
from aqua_tcg.exceptions import InvalidAbilityUseError

if TYPE_CHECKING:
    from aqua_tcg.enums import CardElement

    from .game import Character, Player


class Ability:
    def __init__(
        self, name: str, desc: str, element: CardElement, damage_number: int, target: str = "enemy"
    ) -> None:
        self.name = name
        self.desc = desc
        self.element = element
        self.damage_number = damage_number
        self.target = target

    def use(self, allies: list[Character], enemy: Player) -> None:
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


class Card:
    # Set up the card object
    def __init__(
        self,
        name: str,
        desc: str,
        game: Game,
        element: CardElement,
        basic_desc: str | None = None,
        skill_desc: str | None = None,
        ultimate_desc: str | None = None,
    ) -> None:
        self.name = name
        self.desc = desc
        self.game = game
        self.element = element

        self.basic_desc = basic_desc or f"{self.name} strikes an enemy."
        self.skill_desc = skill_desc or f"{self.name} uses their unique ability."
        self.ultimate_desc = (
            ultimate_desc or f"{self.name} unleashes a devastating ultimate attack."
        )

    def basic(self) -> Ability:
        return Ability(
            name=f"{self.name} Basic",
            desc=self.basic_desc,
            element=self.element,
            damage_number=CARD_BASIC_ATTACK,
        )

    def skill(self) -> Ability:
        return Ability(
            name=f"{self.name} Skill",
            desc=self.skill_desc,
            element=self.element,
            damage_number=CARD_SKILL_ATTACK,
        )

    def ultimate(self) -> Ability:
        return Ability(
            name=f"{self.name} Ultimate",
            desc=self.ultimate_desc,
            element=self.element,
            damage_number=CARD_ULTIMATE_ATTACK,
        )

    def __repr__(self) -> str:
        return "**" + self.name + "* : " + self.desc

    def __str__(self) -> str:
        return "**" + self.name + "* : " + self.desc


class GenshinCard(Card):
    def __init__(
        self,
        name: str,
        desc: str,
        element: CardElement,
        basic_desc: str | None = None,
        skill_desc: str | None = None,
        ultimate_desc: str | None = None,
    ) -> None:
        super().__init__(name, desc, Game.GENSHIN, element, basic_desc, skill_desc, ultimate_desc)


class HSRCard(Card):
    def __init__(
        self,
        name: str,
        desc: str,
        element: CardElement,
        basic_desc: str | None = None,
        skill_desc: str | None = None,
        ultimate_desc: str | None = None,
    ) -> None:
        super().__init__(name, desc, Game.HSR, element, basic_desc, skill_desc, ultimate_desc)


class ZZZCard(Card):
    def __init__(
        self,
        name: str,
        desc: str,
        element: CardElement,
        basic_desc: str | None = None,
        skill_desc: str | None = None,
        ultimate_desc: str | None = None,
    ) -> None:
        super().__init__(name, desc, Game.ZZZ, element, basic_desc, skill_desc, ultimate_desc)
