import nextcord
from nextcord.ext import commands


class Greetings(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(description="Test command")
    async def my_slash_command(self, interaction: nextcord.Interaction):
        await interaction.response.send_message("This is a slash command in a cog!")

    @nextcord.slash_command(description="Reply with pong!")
    async def ping(self, interaction: nextcord.Interaction):
        await interaction.response.send_message(
            f"Pong! The latency is {self.bot.latency}."
        )


def setup(bot):
    bot.add_cog(Greetings(bot))
