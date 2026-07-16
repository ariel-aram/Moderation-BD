from typing import TYPE_CHECKING

import discord
from bd_models.models import BallInstance, Player, balls, specials
from discord import app_commands
from discord.ext import commands

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot


async def ball_autocomplete(interaction: discord.Interaction, current: str):
    matching_balls = [b for b in balls.values() if b.enabled and current.lower() in b.country.lower()]
    return [app_commands.Choice(name=ball.country, value=str(ball.id)) for ball in matching_balls[:25]]


async def special_autocomplete(interaction: discord.Interaction, current: str):
    matching_specials = [s for s in specials.values() if current.lower() in s.name.lower()]
    return [app_commands.Choice(name=special.name, value=str(special.id)) for special in matching_specials[:25]]


class Preview(commands.Cog):
    """Preview card images."""

    def __init__(self, bot: "BallsDexBot"):
        self.bot = bot

    @app_commands.command(name="preview", description="Preview a card image for a ball, even if you don't own it.")
    @app_commands.autocomplete(ball=ball_autocomplete, special=special_autocomplete)
    async def preview(self, interaction: discord.Interaction, ball: str, special: str = None):
        await interaction.response.defer(ephemeral=False)

        try:
            ball_id = int(ball)
            selected_ball = balls.get(ball_id)
            if not selected_ball:
                await interaction.followup.send("Ball not found.", ephemeral=True)
                return
        except ValueError:
            await interaction.followup.send("Invalid ball selection.", ephemeral=True)
            return

        selected_special = None
        if special:
            try:
                special_id = int(special)
                selected_special = specials.get(special_id)
                if not selected_special:
                    await interaction.followup.send("Special not found.", ephemeral=True)
                    return
            except ValueError:
                await interaction.followup.send("Invalid special selection.", ephemeral=True)
                return

        player, _ = await Player.objects.aget_or_create(discord_id=interaction.user.id)
        ownership_query = BallInstance.objects.filter(player=player, ball=selected_ball)
        if selected_special:
            ownership_query = ownership_query.filter(special=selected_special)
        owned_count = await ownership_query.acount()
        ownership_text = f"You own {owned_count}" if owned_count > 0 else "Not owned"

        temp_instance = BallInstance(
            ball=selected_ball,
            special=selected_special,
            health_bonus=0,
            attack_bonus=0,
            favorite=False,
            tradeable=True,
            locked=None,
            extra_data={},
        )

        try:
            buffer = temp_instance.draw_card()
            file = discord.File(buffer, "preview_card.webp")

            embed = discord.Embed(
                title=f"Preview: {selected_ball.country}",
                description=f"Special: {selected_special.name if selected_special else 'Default'}",
                color=discord.Color.blue(),
            )
            embed.set_image(url="attachment://preview_card.webp")
            embed.add_field(name="Ownership", value=ownership_text, inline=True)
            embed.add_field(name="Rarity", value=f"{selected_ball.rarity}%", inline=True)

            await interaction.followup.send(embed=embed, file=file, ephemeral=False)
        except Exception as e:
            await interaction.followup.send(
                f"Failed to generate preview: {str(e)}. This special may not have artwork yet.", ephemeral=True
            )
