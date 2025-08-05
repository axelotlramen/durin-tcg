from __future__ import annotations

import json
import os
import pathlib

from dotenv import load_dotenv

from aqua_tcg.models.user import TCGUser

load_dotenv()
USER_DATA_FILE = pathlib.Path(os.getenv("USER_DATA_FILE", "fallback.json"))


def load_all_users() -> dict[str, TCGUser]:
    if not USER_DATA_FILE.exists():
        return {}
    raw_data = json.loads(USER_DATA_FILE.read_text())
    return {uid: TCGUser(**data) for uid, data in raw_data.items()}


def save_all_users(users: dict[str, TCGUser]) -> None:
    raw = {uid: user.model_dump(mode="json") for uid, user in users.items()}
    USER_DATA_FILE.write_text(json.dumps(raw, indent=4))
