from __future__ import annotations

import logging
import os
import platform
from pathlib import Path

import discord
from discord.ext import commands, tasks
from discord.ext.commands import Context

from utils.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


class AquaBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix="a!", intents=discord.Intents.all(), help_command=None)

        self.initialised = False
        self.logger = logger

    async def _load_cogs(self) -> None:
        for file in Path("./cogs").iterdir():
            if file.suffix == ".py":
                extension = file.stem
                try:
                    await self.load_extension(f"cogs.{extension}")
                    self.logger.info("Loaded extension '%s'", extension)
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    self.logger.error(f"Failed to load extension {extension}\n{exception}")

    @tasks.loop(minutes=5.0)
    async def status_task(self) -> None:
        try:
            song = "「アイドル」by YOASOBI"
            await self.change_presence(
                activity=discord.Activity(type=discord.ActivityType.listening, name=song)
            )
        except Exception as e:
            self.logger.error(f"Status task failed: {e}")

    @status_task.before_loop
    async def before_status_task(self) -> None:
        await self.wait_until_ready()

    async def setup_hook(self) -> None:
        if self.user:
            self.logger.info(f"Logged in as {self.user.name}")
        self.logger.info(f"discord API version: {discord.__version__}")
        self.logger.info(f"Python version: {platform.python_version()}")
        self.logger.info(f"Running on {platform.system()} {platform.release()} ({os.name})")
        self.logger.info("-------------------")

        await self._load_cogs()
        self.status_task.start()

    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.user or message.author.bot:
            return
        await self.process_commands(message)

    async def on_command_completion(self, context: Context) -> None:
        if not context.command:
            return
        full_command_name = context.command.qualified_name
        split = full_command_name.split(" ")
        executed_command = str(split[0])

        if context.guild is not None:
            self.logger.info(
                f"Executed {executed_command} command in {context.guild.name} (ID: {context.guild.id}) by {context.author} (ID: {context.author.id})"
            )
        else:
            self.logger.info(
                f"Executed {executed_command} command by {context.author} (ID: {context.author.id}) in DMs"
            )

    async def on_command_error(self, context: Context, error) -> None:
        raise error
