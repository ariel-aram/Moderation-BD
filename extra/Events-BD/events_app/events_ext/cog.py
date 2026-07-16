from typing import TYPE_CHECKING

import discord
from bd_models.models import BallInstance, Special
from discord import app_commands
from discord.ext import commands

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot


@app_commands.guild_only()
class Events(commands.Cog):
    """
    View information about special events.
    """

    def __init__(self, bot: "BallsDexBot"):
        self.bot = bot

    @app_commands.command()
    async def events(self, interaction: discord.Interaction["BallsDexBot"]):
        """
        List all special events with their details.
        """
        await interaction.response.defer(ephemeral=True)

        specials = [x async for x in Special.objects.order_by("-id").all()]

        if not specials:
            await interaction.followup.send("No special events found in the database.", ephemeral=True)
            return

        embed = discord.Embed(
            title="📅 Special Events", color=discord.Color.blue(), description=f"Total events: {len(specials)}"
        )

        event_list = []

        for special in specials:
            emoji_display = "❓"
            if special.emoji:
                try:
                    emoji_obj = self.bot.get_emoji(int(special.emoji))
                    emoji_display = str(emoji_obj) if emoji_obj else "❓"
                except ValueError:
                    emoji_display = special.emoji

            rarity_percent = special.rarity * 100
            if rarity_percent.is_integer():
                rarity_str = f"{int(rarity_percent)}%"
            else:
                rarity_str = f"{rarity_percent:.2f}%"

            if special.start_date and special.end_date:
                start_timestamp = f"<t:{int(special.start_date.timestamp())}:f>"
                end_timestamp = f"<t:{int(special.end_date.timestamp())}:f>"
                date_range = f"{start_timestamp} - {end_timestamp}"
            else:
                date_range = "Ongoing"

            card_count = await BallInstance.objects.filter(special=special).acount()

            event_line = f"**{special.name}** {emoji_display} • {date_range} • {rarity_str} • {card_count} caught"
            event_list.append(event_line)

        embed.description = "\n\n".join(event_list)

        embed.set_footer(text=f"Total: {len(specials)} events")

        await interaction.followup.send(embed=embed, ephemeral=True)
