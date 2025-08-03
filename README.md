# Discord Verification Bot

A Discord bot for manual user verification that removes entry roles and assigns verified roles via commands.

## Features

- **Manual Verification**: Verify users with a simple command
- **Role Management**: Automatically removes entry roles and assigns verified roles
- **Permission Control**: Commands restricted to users with "Manage Roles" permission
- **Status Checking**: Check verification status of any user
- **Error Handling**: Comprehensive error handling with clear feedback
- **Logging**: Detailed logging of all verification actions
- **Slash Commands**: Supports both text commands (!) and slash commands (/)

## Setup Instructions

### 1. Create a Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to "Bot" section and click "Add Bot"
4. Copy the bot token for later use
5. Enable the following Privileged Gateway Intents:
   - Server Members Intent
   - Message Content Intent

### 2. Bot Permissions

Your bot needs the following permissions:
- `Manage Roles` - To add/remove roles from users
- `Send Messages` - To send command responses
- `Use Slash Commands` - To use slash commands
- `Read Message History` - To process commands

### 3. Server Setup

1. Create two roles in your Discord server:
   - **Entry Role**: Given to new users when they join
   - **Verified Role**: Given to users after manual verification

2. Set up channel permissions:
   - Entry role should have limited access (e.g., only welcome channel)
   - Verified role should have access to all other channels

3. Get role IDs:
   - Enable Developer Mode in Discord (User Settings → Advanced → Developer Mode)
   - Right-click on each role and select "Copy ID"

### 4. Installation

1. Clone or download this bot code
2. Copy `.env.example` to `.env`
3. Fill in your configuration in `.env`:
   ```env
   DISCORD_TOKEN=your_bot_token_here
   ENTRY_ROLE_ID=123456789012345678
   VERIFIED_ROLE_ID=987654321098765432
   