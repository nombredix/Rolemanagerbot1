# Overview

This is a Discord verification bot designed for manual user verification in Discord servers. The bot automates the verification process by managing user roles through commands - removing entry roles from new users and assigning specific verification roles to manually approved members. It supports gender-specific verification with commands +men and +wom, as well as general verification commands, with comprehensive error handling and logging capabilities.

# User Preferences

Preferred communication style: Simple, everyday language.
Language: French

# System Architecture

## Bot Framework
- **Discord.py Library**: Uses the discord.py library with the commands extension for structured command handling
- **Async Architecture**: Built on Python's asyncio for handling Discord's asynchronous API operations
- **Command System**: Dual support for text commands (!) and slash commands (/) to accommodate different user preferences

## Configuration Management
- **Environment-based Config**: Centralized configuration system using environment variables loaded via python-dotenv
- **Validation Layer**: Input validation for required settings like Discord token and role IDs
- **Flexible Settings**: Support for optional configurations like custom command prefixes and guild-specific command syncing

## Role Management System
- **Two-Role Model**: Simple architecture with entry roles (for new users) and verified roles (for approved users)
- **Permission-based Access**: Commands restricted to users with "Manage Roles" Discord permission
- **Automatic Role Swapping**: Seamless removal of entry roles and assignment of verified roles in a single verification action

## Error Handling & Logging
- **Comprehensive Error Handling**: Specific error handling for missing permissions, invalid users, and missing roles
- **Multi-destination Logging**: Dual logging to both file (bot.log) and console with structured formatting
- **Graceful Degradation**: Bot continues operation even when non-critical operations fail

## Bot Lifecycle Management
- **Gateway Intents**: Configured with necessary intents for message content, guild access, and member management
- **Command Synchronization**: Automatic slash command syncing on startup with error recovery
- **Clean Shutdown**: Proper handling of keyboard interrupts and unexpected errors

# External Dependencies

## Discord Platform
- **Discord API**: Primary integration for all bot functionality through discord.py library
- **Discord Developer Portal**: Required for bot token generation and permission configuration
- **Discord Gateway**: Real-time connection for receiving events and command interactions

## Python Libraries
- **discord.py**: Core Discord API wrapper providing bot framework and command handling
- **python-dotenv**: Environment variable management for secure configuration loading
- **asyncio**: Built-in Python library for asynchronous programming support

## Runtime Environment
- **Python 3.7+**: Minimum Python version requirement for discord.py compatibility
- **File System**: Local file system access for logging operations (bot.log file)
- **Environment Variables**: System environment or .env file for configuration storage

## Discord Server Requirements
- **Role Hierarchy**: Bot role must be positioned above the roles it manages in server hierarchy
- **Channel Permissions**: Proper channel permission setup to restrict entry role access
- **Developer Mode**: Required for server administrators to obtain role and guild IDs