from __future__ import annotations

import os

import nextcord
from dotenv import load_dotenv
from nextcord.ext import commands

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
TESTING_GUILD_ID = int(os.getenv("GUILD_ID") or "")

intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True

bot: commands.Bot = commands.Bot(
    command_prefix="a!", intents=intents, default_guild_ids=[TESTING_GUILD_ID]
)


@bot.event
async def on_ready():
    if bot.user:
        print(f"Logged in as {bot.user} (ID: {bot.user.id})")


@bot.command()
async def load(ctx, extension):
    bot.load_extension(f"cogs.{extension}")
    await ctx.send("Loaded cog!")


@bot.command()
async def unload(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")
    await ctx.send("Unloaded cog!")


@bot.command()
async def reload(ctx, extension):
    bot.reload_extension(f"cogs.{extension}")
    await ctx.send("Reloaded cog!")


@bot.command()
async def sync(ctx):
    await bot.sync_application_commands(guild_id=TESTING_GUILD_ID)
    await ctx.send("Synced commands!")


# Load all cogs
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

bot.run(TOKEN)
