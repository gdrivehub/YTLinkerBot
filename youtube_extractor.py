"""
YouTube video description extractor using YouTube Data API v3
"""

import re
import logging
from urllib.parse import urlparse, parse_qs
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import YOUTUBE_API_KEY

logger = logging.getLogger(__name__)

class YouTubeExtractor:
    def __init__(self):
        """Initialize YouTube Data API client"""
        self.youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        # Regex pattern to match HTTPS URLs
        self.https_pattern = re.compile(r'https://[^\s<>"]+', re.IGNORECASE)
    
    def extract_video_id(self, url):
        """
        Extract YouTube video ID from various YouTube URL formats
        
        Args:
            url (str): YouTube URL
            
        Returns:
            str: Video ID or None if invalid
        """
        try:
            # Parse the URL
            parsed_url = urlparse(url)
            
            # Handle different YouTube URL formats
            if parsed_url.hostname in ['www.youtube.com', 'youtube.com', 'm.youtube.com']:
                if parsed_url.path == '/watch':
                    # Standard format: https://www.youtube.com/watch?v=VIDEO_ID
                    query_params = parse_qs(parsed_url.query)
                    return query_params.get('v', [None])[0]
                elif parsed_url.path.startswith('/embed/'):
                    # Embed format: https://www.youtube.com/embed/VIDEO_ID
                    return parsed_url.path.split('/embed/')[-1].split('?')[0]
                elif parsed_url.path.startswith('/v/'):
                    # Old format: https://www.youtube.com/v/VIDEO_ID
                    return parsed_url.path.split('/v/')[-1].split('?')[0]
            elif parsed_url.hostname in ['youtu.be']:
                # Short format: https://youtu.be/VIDEO_ID
                return parsed_url.path[1:].split('?')[0]
            
            return None
        except Exception as e:
            logger.error(f"Error extracting video ID from URL {url}: {str(e)}")
            return None
    
    def get_video_description(self, video_id):
        """
        Fetch video description using YouTube Data API v3
        
        Args:
            video_id (str): YouTube video ID
            
        Returns:
            tuple: (success: bool, description: str or error_message: str)
        """
        try:
            # Make API request to get video details
            request = self.youtube.videos().list(
                part='snippet',
                id=video_id,
                fields='items(snippet(title,description))'
            )
            response = request.execute()
            
            # Check if video exists
            if not response.get('items'):
                return False, "Video not found. The video might be private, deleted, or the URL is invalid."
            
            # Extract description
            video_data = response['items'][0]
            title = video_data['snippet'].get('title', 'Unknown Title')
            description = video_data['snippet'].get('description', '')
            
            logger.info(f"Successfully fetched description for video: {title}")
            return True, description
            
        except HttpError as e:
            error_details = e.error_details[0] if e.error_details else {}
            reason = error_details.get('reason', 'Unknown error')
            
            if e.resp.status == 403:
                if 'quotaExceeded' in reason:
                    return False, "YouTube API quota exceeded. Please try again later."
                else:
                    return False, "Access forbidden. The video might be private or restricted."
            elif e.resp.status == 404:
                return False, "Video not found. Please check the URL and try again."
            else:
                return False, f"YouTube API error: {reason}"
                
        except Exception as e:
            logger.error(f"Unexpected error fetching video description: {str(e)}")
            return False, f"An unexpected error occurred: {str(e)}"
    
    def extract_https_links(self, text):
        """
        Extract all HTTPS links from text using regex
        
        Args:
            text (str): Text to extract links from
            
        Returns:
            list: List of unique HTTPS URLs
        """
        if not text:
            return []
        
        # Find all HTTPS URLs
        links = self.https_pattern.findall(text)
        
        # Clean up links (remove trailing punctuation that might be captured)
        cleaned_links = []
        for link in links:
            # Remove common trailing punctuation
            link = re.sub(r'[.,;:!?)}\]]+$', '', link)
            if link and link not in cleaned_links:
                cleaned_links.append(link)
        
        return cleaned_links
    
    def process_youtube_url(self, url):
        """
        Complete process: extract video ID, get description, extract HTTPS links
        
        Args:
            url (str): YouTube URL
            
        Returns:
            tuple: (success: bool, links: list or error_message: str)
        """
        # Extract video ID
        video_id = self.extract_video_id(url)
        if not video_id:
            return False, "Invalid YouTube URL format. Please provide a valid YouTube video URL."
        
        # Get video description
        success, description = self.get_video_description(video_id)
        if not success:
            return False, description
        
        # Extract HTTPS links
        links = self.extract_https_links(description)
        
        if not links:
            return True, []  # Success but no links found
        
        return True, links
