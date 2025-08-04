from __future__ import annotations

from pydantic import BaseModel, Field

from datetime import datetime, UTC


class CardDeck(BaseModel):
    cards: list[str] = Field(default_factory=list)


class CardSettings(BaseModel):
    card_name: str
    card_frame: str = "default"


class TCGUser(BaseModel):
    owned_cards: list[str] = Field(default_factory=list)
    decks: list[CardDeck] = Field(default_factory=list)
    currency: int = 0
    card_settings: list[CardSettings] = Field(default_factory=list)
    start_date: datetime = Field(default_factory=lambda: datetime.now(UTC))
