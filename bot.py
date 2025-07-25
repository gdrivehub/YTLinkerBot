"""
Telegram bot for extracting HTTPS links from YouTube video descriptions
"""

import logging
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
from youtube_extractor import YouTubeExtractor
from link_filter import LinkFilter
from config import BOT_TOKEN

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class YouTubeLinkBot:
    def __init__(self):
        """Initialize the bot with YouTube extractor and link filter"""
        self.youtube_extractor = YouTubeExtractor()
        self.link_filter = LinkFilter()
        
        # YouTube URL pattern for validation
        self.youtube_url_pattern = re.compile(
            r'(?:https?://)?(?:www\.)?(?:youtube\.com/(?:watch\?v=|embed/|v/)|youtu\.be/)[\w-]+',
            re.IGNORECASE
        )
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        welcome_message = f"""
🎥 **YouTube Link Extractor Bot**

Hello {user.first_name}! I can extract HTTPS links from YouTube video descriptions.

**How to use:**
1. Send me any YouTube video URL
2. I'll fetch the video description and extract all HTTPS links
3. You can customize which links to filter out

**Commands:**
• `/filter <keywords>` - Set filter words (space-separated)
• `/addfilter <keyword>` - Add a single filter word
• `/removefilter <keyword>` - Remove a filter word
• `/showfilter` - Show current filter settings
• `/clearfilter` - Clear all filters
• `/help` - Show this help message

**Example:**
Send: `https://youtu.be/dQw4w9WgXcQ`
I'll extract all HTTPS links from that video's description!

Filter words help exclude unwanted domains (like spam links).
        """
        await update.message.reply_text(welcome_message, parse_mode=ParseMode.MARKDOWN)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        await self.start_command(update, context)
    
    async def filter_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /filter command to set filter words"""
        user_id = update.effective_user.id
        
        if not context.args:
            # Show current filter status
            status = self.link_filter.get_filter_status(user_id)
            await update.message.reply_text(status, parse_mode=ParseMode.MARKDOWN)
            return
        
        # Set new filter words
        filter_words = context.args
        self.link_filter.set_user_filters(user_id, filter_words)
        
        if filter_words:
            filter_list = "\n".join([f"• `{word}`" for word in filter_words])
            message = f"✅ **Filter updated!**\n\n**Now filtering out links containing:**\n{filter_list}"
        else:
            message = "✅ **All filters cleared!**\nAll HTTPS links will now be shown."
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def addfilter_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /addfilter command to add a single filter word"""
        user_id = update.effective_user.id
        
        if not context.args:
            await update.message.reply_text(
                "❌ Please provide a keyword to filter.\n\n**Usage:** `/addfilter keyword`",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        keyword = " ".join(context.args).strip()
        current_filters = self.link_filter.get_user_filters(user_id)
        
        if keyword.lower() in current_filters:
            await update.message.reply_text(
                f"ℹ️ `{keyword}` is already in your filter list.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        self.link_filter.add_filter_word(user_id, keyword)
        await update.message.reply_text(
            f"✅ Added `{keyword}` to your filter list.\nLinks containing this keyword will be excluded.",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def removefilter_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /removefilter command to remove a filter word"""
        user_id = update.effective_user.id
        
        if not context.args:
            await update.message.reply_text(
                "❌ Please provide a keyword to remove.\n\n**Usage:** `/removefilter keyword`",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        keyword = " ".join(context.args).strip()
        removed = self.link_filter.remove_filter_word(user_id, keyword)
        
        if removed:
            await update.message.reply_text(
                f"✅ Removed `{keyword}` from your filter list.",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.message.reply_text(
                f"ℹ️ `{keyword}` was not found in your filter list.",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def showfilter_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /showfilter command to show current filter settings"""
        user_id = update.effective_user.id
        status = self.link_filter.get_filter_status(user_id)
        await update.message.reply_text(status, parse_mode=ParseMode.MARKDOWN)
    
    async def clearfilter_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /clearfilter command to clear all filters"""
        user_id = update.effective_user.id
        self.link_filter.clear_user_filters(user_id)
        await update.message.reply_text(
            "✅ **All filters cleared!**\nAll HTTPS links will now be shown.",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages (YouTube URLs)"""
        user_id = update.effective_user.id
        message_text = update.message.text.strip()
        
        # Check if message contains a YouTube URL
        if not self.youtube_url_pattern.search(message_text):
            await update.message.reply_text(
                "❌ Please send a valid YouTube video URL.\n\n**Supported formats:**\n"
                "• https://www.youtube.com/watch?v=VIDEO_ID\n"
                "• https://youtu.be/VIDEO_ID\n"
                "• https://www.youtube.com/embed/VIDEO_ID"
            )
            return
        
        # Extract YouTube URL from message
        youtube_urls = self.youtube_url_pattern.findall(message_text)
        youtube_url = youtube_urls[0]
        
        # Send processing message
        processing_msg = await update.message.reply_text("🔄 Processing YouTube video...")
        
        try:
            # Extract links from YouTube video
            success, result = self.youtube_extractor.process_youtube_url(youtube_url)
            
            if not success:
                await processing_msg.edit_text(f"❌ **Error:** {result}")
                return
            
            links = result
            
            if not links:
                await processing_msg.edit_text(
                    "ℹ️ **No HTTPS links found** in this video's description."
                )
                return
            
            # Apply user filters
            filtered_links, excluded_count = self.link_filter.filter_links(user_id, links)
            
            # Format response
            if not filtered_links:
                filter_info = f"\n\n🔒 All {len(links)} link(s) were filtered out based on your settings." if excluded_count > 0 else ""
                await processing_msg.edit_text(
                    f"ℹ️ **No links to display** after applying filters.{filter_info}\n\n"
                    "Use `/showfilter` to check your current filter settings."
                )
                return
            
            # Prepare the response message
            response_parts = [f"🔗 **Found {len(filtered_links)} HTTPS link(s):**\n"]
            
            # Add links (limit to prevent message length issues)
            for i, link in enumerate(filtered_links[:20], 1):  # Limit to 20 links
                response_parts.append(f"{i}. {link}")
            
            if len(filtered_links) > 20:
                response_parts.append(f"\n... and {len(filtered_links) - 20} more links")
            
            # Add filter information
            if excluded_count > 0:
                response_parts.append(f"\n🔒 {excluded_count} link(s) filtered out")
            
            total_found = len(links)
            if total_found != len(filtered_links):
                response_parts.append(f"📊 Total found: {total_found}, Shown: {len(filtered_links)}")
            
            response_message = "\n".join(response_parts)
            
            # Check if message is too long for Telegram
            if len(response_message) > 4000:
                # Split into multiple messages
                link_text = "\n".join([f"{i}. {link}" for i, link in enumerate(filtered_links[:15], 1)])
                first_message = f"🔗 **Found {len(filtered_links)} HTTPS link(s):**\n\n{link_text}"
                
                if excluded_count > 0:
                    first_message += f"\n\n🔒 {excluded_count} link(s) filtered out"
                
                await processing_msg.edit_text(first_message)
                
                # Send remaining links if any
                if len(filtered_links) > 15:
                    remaining_links = filtered_links[15:30]  # Next 15 links
                    remaining_text = "\n".join([f"{i}. {link}" for i, link in enumerate(remaining_links, 16)])
                    await update.message.reply_text(f"**Continued:**\n\n{remaining_text}")
            else:
                await processing_msg.edit_text(response_message)
            
        except Exception as e:
            logger.error(f"Error processing YouTube URL: {str(e)}")
            await processing_msg.edit_text(
                f"❌ **An unexpected error occurred:** {str(e)}\n\n"
                "Please try again later or contact support if the issue persists."
            )
    
    def create_application(self):
        """Create and configure the Telegram bot application"""
        # Create application
        app = Application.builder().token(BOT_TOKEN).build()
        
        # Add handlers
        app.add_handler(CommandHandler("start", self.start_command))
        app.add_handler(CommandHandler("help", self.help_command))
        app.add_handler(CommandHandler("filter", self.filter_command))
        app.add_handler(CommandHandler("addfilter", self.addfilter_command))
        app.add_handler(CommandHandler("removefilter", self.removefilter_command))
        app.add_handler(CommandHandler("showfilter", self.showfilter_command))
        app.add_handler(CommandHandler("clearfilter", self.clearfilter_command))
        
        # Handle text messages (YouTube URLs)
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        return app
