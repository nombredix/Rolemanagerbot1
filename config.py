"""
Configuration module for Discord Verification Bot
Handles environment variables and bot settings.
"""

import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

class Config:
    """Configuration class to manage bot settings."""
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        # Load environment variables from .env file
        load_dotenv()
        
        # Discord Bot Token (required)
        self.DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
        if not self.DISCORD_TOKEN:
            raise ValueError("DISCORD_TOKEN environment variable is required")
        
        # Role IDs (required)
        entry_role_id = os.getenv('ENTRY_ROLE_ID')
        verified_role_id = os.getenv('VERIFIED_ROLE_ID')
        
        if not entry_role_id:
            raise ValueError("ENTRY_ROLE_ID environment variable is required")
        if not verified_role_id:
            raise ValueError("VERIFIED_ROLE_ID environment variable is required")
        
        try:
            self.ENTRY_ROLE_ID = int(entry_role_id)
            self.VERIFIED_ROLE_ID = int(verified_role_id)
        except ValueError:
            raise ValueError("Role IDs must be valid integers")
        
        # Optional settings
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
        self.COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '!')
        
        # Guild ID (optional - for faster command sync)
        guild_id = os.getenv('GUILD_ID')
        self.GUILD_ID = int(guild_id) if guild_id else None
        
        logger.info("Configuration loaded successfully")
        logger.info(f"Entry Role ID: {self.ENTRY_ROLE_ID}")
        logger.info(f"Verified Role ID: {self.VERIFIED_ROLE_ID}")
        logger.info(f"Command Prefix: {self.COMMAND_PREFIX}")
        
    def validate(self):
        """Validate configuration settings."""
        if self.ENTRY_ROLE_ID == self.VERIFIED_ROLE_ID:
            raise ValueError("Entry role and verified role cannot be the same")
        
        return True
