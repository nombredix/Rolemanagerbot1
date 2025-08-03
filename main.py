"""
Discord Verification Bot - Entry Point
Main script to run the Discord bot for manual user verification.
"""

import asyncio
import logging
from bot import VerificationBot
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('bot.log'),
              logging.StreamHandler()])

logger = logging.getLogger(__name__)


async def main():
    """Main function to initialize and run the bot."""
    try:
        # Load configuration
        config = Config()

        # Initialize bot
        bot = VerificationBot(config)

        logger.info("Starting Discord Verification Bot...")

        # Run the bot
        await bot.start(config.DISCORD_TOKEN)

    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
