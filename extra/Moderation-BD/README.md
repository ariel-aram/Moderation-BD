# Moderation-BD

A moderation extra package for [Ballsdex v3](https://github.com/Ballsdex-Team/BallsDex-DiscordBot).

Provides slash commands for common moderation actions: kick, ban, unban, mute, unmute, warn, purge, slowmode, lock/unlock channels, and nickname management. Warnings are persisted in the database and visible in the admin panel. And blah blah blah.

The base for this extra package comes from [molteencreates/BallsDex-DiscordBot-Moderation-Package](https://github.com/molteencreates/BallsDex-DiscordBot-Moderation-Package), with some modifications to fit the Ballsdex v3 ecosystem. Therefore, the proper credits goes to [**molteencreates**](https://github.com/molteencreates) for the original package.

## Disclaimer

For this extra package to work, you must enable the following permissions for the bot:

- `Kick Members`
- `Ban Members`
- `Manage Roles`
- `Manage Channels`
- `Change Nickname`

If you leave these permissions disabled, then bye bye, get out of this repository. `>:(`

## Commands

All commands are grouped under `/moderation`:

| Command | Description |
|---------|-------------|
| `/moderation kick` | Kick a user from the server |
| `/moderation ban` | Ban a user from the server |
| `/moderation unban` | Unban a user by tag (Explosives#6969) |
| `/moderation mute` | Mute a user with a "Muted" role |
| `/moderation unmute` | Unmute a user |
| `/moderation setmutedrole` | Set the role used for muting members |
| `/moderation warn` | Warn a user (persisted in database) |
| `/moderation warnings` | List warnings for a user |
| `/moderation clearwarnings` | Clear all warnings for a user |
| `/moderation purge` | Purge messages in the channel |
| `/moderation slowmode` | Set slowmode in the channel |
| `/moderation lock` | Lock the channel |
| `/moderation unlock` | Unlock the channel |
| `/moderation nickname` | Change a user's nickname |

## Installation

### Docker

Add the following to your `config/extra.toml`:

```toml
[[ballsdex.packages]]
location = "code/extra/Moderation-BD"
path = "moderation_app"
enabled = true
editable = true
```

Then rebuild and restart:

```bash
docker compose up --build
```

## Requirements

- Ballsdex >= 3.0.0
- Python >= 3.14

## License

MIT
