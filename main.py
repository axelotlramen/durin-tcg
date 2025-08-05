from __future__ import annotations

from aqua_tcg.bot import AquaBot
from aqua_tcg.config import CONFIG

bot = AquaBot()


bot.run(CONFIG.discord_token)
