#!/usr/bin/env python3
"""
Simple Telegram Bot without telegram.ext dependencies
Uses direct HTTP requests to Telegram Bot API
"""

import asyncio
import aiohttp
import json
import logging
from urllib.parse import quote
from youtube_extractor import YouTubeExtractor
from link_filter import LinkFilter
from config import BOT_TOKEN

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleTelegramBot:
    def __init__(self):
        self.token = BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.youtube_extractor = YouTubeExtractor()
        self.link_filter = LinkFilter()
        self.session = None
        
    async def start_session(self):
        """Start HTTP session"""
        self.session = aiohttp.ClientSession()
    
    async def close_session(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
    
    async def send_message(self, chat_id, text, parse_mode=None):
        """Send message to chat"""
        url = f"{self.base_url}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": text
        }
        if parse_mode:
            data["parse_mode"] = parse_mode
            
        async with self.session.post(url, data=data) as response:
            return await response.json()
    
    async def get_updates(self, offset=None):
        """Get updates from Telegram"""
        url = f"{self.base_url}/getUpdates"
        params = {"timeout": 30}
        if offset:
            params["offset"] = offset
            
        async with self.session.get(url, params=params) as response:
            return await response.json()
    
    async def handle_start(self, chat_id):
        """Handle /start command"""
        message = """🎥 *YouTube Link Extractor Bot*

Welcome! Send me a YouTube video URL and I'll extract all HTTPS links from the video description.

*Commands:*
• `/start` - Show this help
• `/filter word1 word2` - Set filter words to exclude
• `/addfilter word` - Add a filter word
• `/removefilter word` - Remove a filter word
• `/showfilter` - Show current filters
• `/clearfilter` - Clear all filters

*Example:*
Just send: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`

The bot supports all YouTube URL formats and applies customizable filtering to exclude unwanted links."""
        
        await self.send_message(chat_id, message, "Markdown")
    
    async def handle_filter_command(self, chat_id, user_id, args):
        """Handle filter commands"""
        if not args:
            await self.send_message(chat_id, "Usage: /filter word1 word2 word3")
            return
            
        filter_words = args.lower().split()
        self.link_filter.set_user_filters(user_id, filter_words)
        
        message = f"✅ Filter updated!\nBlocking links containing: {', '.join(filter_words)}"
        await self.send_message(chat_id, message)
    
    async def handle_youtube_url(self, chat_id, user_id, url):
        """Handle YouTube URL processing"""
        # Send processing message
        await self.send_message(chat_id, "🔄 Processing YouTube video...")
        
        # Extract links
        success, result = self.youtube_extractor.process_youtube_url(url)
        
        if not success:
            await self.send_message(chat_id, f"❌ Error: {result}")
            return
        
        links = result
        if not links:
            await self.send_message(chat_id, "ℹ️ No HTTPS links found in video description.")
            return
        
        # Apply filters
        filtered_links, excluded_count = self.link_filter.filter_links(user_id, links)
        
        # Format response
        if filtered_links:
            response = f"✅ Found {len(links)} HTTPS links"
            if excluded_count > 0:
                response += f" ({excluded_count} filtered out)"
            response += ":\n\n"
            
            for i, link in enumerate(filtered_links, 1):
                response += f"{i}. {link}\n"
        else:
            response = f"🔒 All {len(links)} links were filtered out.\nUse /showfilter to see your current filters."
        
        await self.send_message(chat_id, response)
    
    async def handle_message(self, message):
        """Handle incoming message"""
        chat_id = message["chat"]["id"]
        user_id = message["from"]["id"]
        text = message.get("text", "")
        
        logger.info(f"Received message from {user_id}: {text[:50]}...")
        
        if text.startswith("/start"):
            await self.handle_start(chat_id)
        elif text.startswith("/filter"):
            args = text[7:].strip()  # Remove "/filter"
            await self.handle_filter_command(chat_id, user_id, args)
        elif "youtube.com" in text or "youtu.be" in text:
            await self.handle_youtube_url(chat_id, user_id, text.strip())
        else:
            await self.send_message(chat_id, "Please send a YouTube URL or use /start for help.")
    
    async def run(self):
        """Main bot loop"""
        await self.start_session()
        
        # Test connection
        try:
            response = await self.get_updates()
            if response.get("ok"):
                logger.info("✅ Bot connected successfully!")
            else:
                logger.error(f"❌ Bot connection failed: {response}")
                return
        except Exception as e:
            logger.error(f"❌ Connection error: {e}")
            return
        
        offset = None
        logger.info("🤖 Bot is running and listening for messages...")
        
        try:
            while True:
                updates = await self.get_updates(offset)
                
                if updates.get("ok") and updates.get("result"):
                    for update in updates["result"]:
                        offset = update["update_id"] + 1
                        
                        if "message" in update:
                            try:
                                await self.handle_message(update["message"])
                            except Exception as e:
                                logger.error(f"Error handling message: {e}")
                                
        except KeyboardInterrupt:
            logger.info("🛑 Bot stopped by user")
        except Exception as e:
            logger.error(f"❌ Bot error: {e}")
        finally:
            await self.close_session()

async def main():
    """Main function"""
    bot = SimpleTelegramBot()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())