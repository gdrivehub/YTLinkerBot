"""
Main entry point for the YouTube Link Extractor Telegram Bot
"""

import asyncio
import logging
from bot import YouTubeLinkBot
from config import HOST, PORT

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    """Main function to run the Telegram bot"""
    try:
        # Create bot instance
        youtube_bot = YouTubeLinkBot()
        
        # Create application
        app = youtube_bot.create_application()
        
        logger.info("Starting YouTube Link Extractor Bot...")
        logger.info(f"Bot will run on {HOST}:{PORT}")
        
        # Start the bot with polling (more reliable than webhooks for this use case)
        await app.run_polling(
            drop_pending_updates=True,
            allowed_updates=['message', 'callback_query']
        )
        
    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        # Run the bot
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {str(e)}")
        exit(1)
