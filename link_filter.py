"""
Link filtering system for customizable link exclusion
"""

import re
from config import DEFAULT_FILTER_WORDS

class LinkFilter:
    def __init__(self):
        """Initialize the link filter with user-specific filter preferences"""
        # Dictionary to store user-specific filter words
        # Format: {user_id: [list_of_filter_words]}
        self.user_filters = {}
    
    def get_user_filters(self, user_id):
        """
        Get filter words for a specific user
        
        Args:
            user_id (int): Telegram user ID
            
        Returns:
            list: List of filter words for the user
        """
        return self.user_filters.get(user_id, DEFAULT_FILTER_WORDS.copy())
    
    def set_user_filters(self, user_id, filter_words):
        """
        Set filter words for a specific user
        
        Args:
            user_id (int): Telegram user ID
            filter_words (list): List of words/domains to filter out
        """
        # Convert to lowercase for case-insensitive matching
        self.user_filters[user_id] = [word.lower().strip() for word in filter_words if word.strip()]
    
    def add_filter_word(self, user_id, word):
        """
        Add a single filter word for a user
        
        Args:
            user_id (int): Telegram user ID
            word (str): Word/domain to add to filter
        """
        current_filters = self.get_user_filters(user_id)
        word = word.lower().strip()
        if word and word not in current_filters:
            current_filters.append(word)
            self.user_filters[user_id] = current_filters
    
    def remove_filter_word(self, user_id, word):
        """
        Remove a single filter word for a user
        
        Args:
            user_id (int): Telegram user ID
            word (str): Word/domain to remove from filter
            
        Returns:
            bool: True if word was removed, False if word wasn't in filter
        """
        current_filters = self.get_user_filters(user_id)
        word = word.lower().strip()
        if word in current_filters:
            current_filters.remove(word)
            self.user_filters[user_id] = current_filters
            return True
        return False
    
    def clear_user_filters(self, user_id):
        """
        Clear all filter words for a user (reset to empty)
        
        Args:
            user_id (int): Telegram user ID
        """
        self.user_filters[user_id] = []
    
    def filter_links(self, user_id, links):
        """
        Filter links based on user's filter preferences
        
        Args:
            user_id (int): Telegram user ID
            links (list): List of HTTPS links to filter
            
        Returns:
            tuple: (filtered_links: list, excluded_count: int)
        """
        if not links:
            return [], 0
        
        filter_words = self.get_user_filters(user_id)
        if not filter_words:
            return links, 0
        
        filtered_links = []
        excluded_count = 0
        
        for link in links:
            # Check if link contains any filter words (case-insensitive)
            should_exclude = False
            link_lower = link.lower()
            
            for filter_word in filter_words:
                if filter_word in link_lower:
                    should_exclude = True
                    break
            
            if should_exclude:
                excluded_count += 1
            else:
                filtered_links.append(link)
        
        return filtered_links, excluded_count
    
    def get_filter_status(self, user_id):
        """
        Get a formatted string showing current filter status for a user
        
        Args:
            user_id (int): Telegram user ID
            
        Returns:
            str: Formatted filter status message
        """
        filter_words = self.get_user_filters(user_id)
        
        if not filter_words:
            return "🔓 **Filter Status**: No filters active\nAll HTTPS links will be shown."
        
        filter_list = "\n".join([f"• `{word}`" for word in filter_words])
        return f"🔒 **Filter Status**: {len(filter_words)} filter(s) active\n\n**Excluded keywords:**\n{filter_list}\n\nLinks containing these keywords will be excluded from results."
