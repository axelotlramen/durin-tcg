from __future__ import annotations

from durin_tcg.bot import DurinBot
from durin_tcg.config import CONFIG

bot = DurinBot()


bot.run(CONFIG.discord_token)
