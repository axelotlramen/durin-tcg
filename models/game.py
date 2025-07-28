from __future__ import annotations

from typing import TYPE_CHECKING

from attr import dataclass

if TYPE_CHECKING:
    from enums import CardDamageType


@dataclass(kw_only=True)
class Character:
    current_hp: int
    current_shield: int = 0

    @property
    def final_hp(self) -> int:
        return self.current_hp + self.current_shield


@dataclass(kw_only=True)
class Damage:
    enemy_index: int
    damage: int
    damage_type: CardDamageType
