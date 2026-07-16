import discord
from ballsdex.core.utils.transformers import BallTransformer
from bd_models.models import Ball, BallInstance
from discord import app_commands
from discord.ext import commands
from django.core.exceptions import ObjectDoesNotExist

from ..models import WishlistItem


@app_commands.guild_only()
class Wishlist(commands.GroupCog, group_name="wishlist"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="view", description="View your wishlist or another user's wishlist.")
    async def view(self, interaction: discord.Interaction, user: discord.User | None = None):
        target = user or interaction.user

        items = [item async for item in WishlistItem.objects.filter(user_id=target.id)]

        if not items:
            if target == interaction.user:
                await interaction.response.send_message("Your wishlist is empty.", ephemeral=True)
            else:
                await interaction.response.send_message(f"{target.display_name}'s wishlist is empty.", ephemeral=True)
            return

        lines = []
        for item in items:
            ball = await Ball.objects.filter(country__iexact=item.ball_country).afirst()
            owned = await BallInstance.objects.filter(player__discord_id=target.id, ball=ball).acount() if ball else 0
            lines.append(f"{ball.country if ball else item.ball_country} ({owned} owned)")

        embed = discord.Embed(
            title=f"{target.display_name}'s Wishlist",
            description="\n".join(lines),
            color=discord.Color.gold(),
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="add", description="Add a countryball to your wishlist.")
    async def add(self, interaction: discord.Interaction, countryball: BallTransformer):
        exists = await WishlistItem.objects.filter(
            user_id=interaction.user.id, ball_country=countryball.country
        ).aexists()

        if exists:
            await interaction.response.send_message(
                f"{countryball.country} is already in your wishlist.", ephemeral=True
            )
            return

        await WishlistItem.objects.acreate(user_id=interaction.user.id, ball_country=countryball.country)
        await interaction.response.send_message(f"Added {countryball.country} to your wishlist.", ephemeral=True)

    @app_commands.command(name="remove", description="Remove a countryball from your wishlist.")
    async def remove(self, interaction: discord.Interaction, countryball: BallTransformer):
        try:
            item = await WishlistItem.objects.aget(user_id=interaction.user.id, ball_country=countryball.country)
        except ObjectDoesNotExist:
            await interaction.response.send_message(f"{countryball.country} is not in your wishlist.", ephemeral=True)
            return

        await item.adelete()
        await interaction.response.send_message(f"Removed {countryball.country} from your wishlist.", ephemeral=True)

    @app_commands.command(name="purge", description="Clear your entire wishlist.")
    async def purge(self, interaction: discord.Interaction):
        items = WishlistItem.objects.filter(user_id=interaction.user.id)
        count = await items.acount()

        if count == 0:
            await interaction.response.send_message("Your wishlist is already empty.", ephemeral=True)
            return

        await items.adelete()
        await interaction.response.send_message(f"Cleared {count} item(s) from your wishlist.", ephemeral=True)
