import logging
import random
from typing import TYPE_CHECKING

import discord
from bd_models.models import Ball, BallInstance, Player, Special
from discord import app_commands
from discord.ext import commands
from django.utils import timezone

from ..models import AdventClaim, AdventDayConfig, RewardType

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot

log = logging.getLogger("advent_app.advent_ext")


class AdventCalendar(commands.Cog):
    """Advent Calendar cog for Ballsdex v3."""

    group = app_commands.Group(name="advent", description="Advent Calendar commands.")

    def __init__(self, bot: "BallsDexBot"):
        self.bot = bot

    @group.command(name="claim", description="Claim your daily advent calendar reward.")
    async def claim(self, interaction: discord.Interaction["BallsDexBot"]):
        user_id = interaction.user.id
        blacklist = getattr(self.bot, "blacklist", set())
        if user_id in blacklist:
            await interaction.response.send_message(
                "You are blacklisted and cannot claim advent rewards.", ephemeral=True
            )
            return

        now = timezone.now()
        today = now.day

        day_config = (
            await AdventDayConfig.objects.filter(day=today, enabled=True).select_related("ball", "special").afirst()
        )
        if not day_config:
            await interaction.response.send_message(
                "No advent reward is configured for today. Check back later!", ephemeral=True
            )
            return

        player, _ = await Player.objects.aget_or_create(discord_id=user_id)

        already_claimed = await AdventClaim.objects.filter(player=player, day=today).aexists()
        if already_claimed:
            await interaction.response.send_message("You have already claimed today's advent reward!", ephemeral=True)
            return

        reward_type = day_config.reward_type
        ball_obj = day_config.ball
        special_obj = day_config.special

        embed = discord.Embed(title=f"Advent Calendar - Day {today}", color=discord.Color.gold())
        reward_lines = []

        if reward_type == RewardType.RANDOM_SPECIAL.value:
            enabled_balls = [b async for b in Ball.enabled_objects.all()]
            all_specials = [s async for s in Special.objects.all()]
            if enabled_balls and all_specials:
                chosen_ball = random.choice(enabled_balls)
                chosen_special = random.choice(all_specials)
                await BallInstance.objects.acreate(
                    ball=chosen_ball,
                    player=player,
                    special=chosen_special,
                )
                emoji = ""
                if chosen_ball.emoji_id and interaction.client:
                    emoji_obj = interaction.client.get_emoji(chosen_ball.emoji_id)
                    if emoji_obj:
                        emoji = f"{emoji_obj} "
                reward_lines.append(f"{emoji}{chosen_ball.country} + **{chosen_special.name}**")
            else:
                reward_lines.append("No balls or specials available. Contact an admin.")

        elif reward_type == RewardType.SELECTED_BALL.value:
            if ball_obj:
                await BallInstance.objects.acreate(
                    ball=ball_obj,
                    player=player,
                )
                emoji = ""
                if ball_obj.emoji_id and interaction.client:
                    emoji_obj = interaction.client.get_emoji(ball_obj.emoji_id)
                    if emoji_obj:
                        emoji = f"{emoji_obj} "
                reward_lines.append(f"{emoji}{ball_obj.country}")
            else:
                reward_lines.append("No ball configured for today. Contact an admin.")

        elif reward_type == RewardType.SELECTED_BALL_WITH_SPECIAL.value:
            if ball_obj:
                await BallInstance.objects.acreate(
                    ball=ball_obj,
                    player=player,
                    special=special_obj,
                )
                emoji = ""
                if ball_obj.emoji_id and interaction.client:
                    emoji_obj = interaction.client.get_emoji(ball_obj.emoji_id)
                    if emoji_obj:
                        emoji = f"{emoji_obj} "
                special_name = special_obj.name if special_obj else "None"
                reward_lines.append(f"{emoji}{ball_obj.country} with {special_name}")
            else:
                reward_lines.append("No ball configured for today. Contact an admin.")

        await AdventClaim.objects.acreate(player=player, day=today)

        if reward_lines:
            embed.add_field(name="Reward", value="\n".join(reward_lines), inline=False)
        embed.add_field(name="Claimed by", value=interaction.user.mention, inline=False)

        if day_config.label:
            embed.set_footer(text=day_config.label)

        await interaction.response.send_message(embed=embed)

    @group.command(name="calendar", description="View your advent calendar progress.")
    async def calendar(self, interaction: discord.Interaction["BallsDexBot"]):
        user_id = interaction.user.id
        blacklist = getattr(self.bot, "blacklist", set())
        if user_id in blacklist:
            await interaction.response.send_message("You are blacklisted.", ephemeral=True)
            return

        player = await Player.objects.filter(discord_id=user_id).afirst()
        if not player:
            await interaction.response.send_message("You haven't claimed any advent rewards yet.", ephemeral=True)
            return

        claimed_days = []
        async for claim in AdventClaim.objects.filter(player=player).order_by("day"):
            claimed_days.append(claim.day)

        all_configs = [x async for x in AdventDayConfig.objects.filter(enabled=True).order_by("day")]

        lines = []
        for config in all_configs:
            emoji = "🎁" if config.day in claimed_days else "⬛"
            emoji_part = ""
            if config.day in claimed_days:
                emoji_part = f"**[Day {config.day}]**"
            else:
                emoji_part = f"Day {config.day}"
            label = f" - {config.label}" if config.label else ""
            lines.append(f"{emoji} {emoji_part}{label}")

        embed = discord.Embed(
            title="Advent Calendar Progress",
            description="\n".join(lines) if lines else "No days configured.",
            color=discord.Color.green(),
        )
        embed.set_footer(text=f"{len(claimed_days)} / {len(all_configs)} days claimed")
        await interaction.response.send_message(embed=embed)
