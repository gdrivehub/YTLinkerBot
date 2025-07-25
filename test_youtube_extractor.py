#!/usr/bin/env python3
"""
Simple test script to demonstrate YouTube link extraction functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from youtube_extractor import YouTubeExtractor
from link_filter import LinkFilter

def test_youtube_extraction():
    """Test the YouTube link extraction functionality"""
    
    print("🎥 YouTube Link Extractor Bot - Test Demo")
    print("=" * 50)
    
    # Initialize components
    youtube_extractor = YouTubeExtractor()
    link_filter = LinkFilter()
    
    # Test with a sample YouTube URL
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up
    print(f"\n📺 Testing with YouTube URL: {test_url}")
    
    # Extract links from the video
    print("\n🔄 Extracting links from video description...")
    success, result = youtube_extractor.process_youtube_url(test_url)
    
    if success:
        links = result
        print(f"✅ Successfully extracted {len(links)} HTTPS links from video description")
        
        if links:
            print("\n🔗 Found links:")
            for i, link in enumerate(links, 1):
                print(f"  {i}. {link}")
            
            # Test filtering functionality
            print("\n🔒 Testing link filtering...")
            user_id = 12345  # Test user ID
            
            # Set some filter words
            filter_words = ['facebook.com', 'twitter.com', 'spam.com']
            link_filter.set_user_filters(user_id, filter_words)
            
            # Apply filters
            filtered_links, excluded_count = link_filter.filter_links(user_id, links)
            
            print(f"🔒 Applied filters: {filter_words}")
            print(f"📊 Results: {len(filtered_links)} links shown, {excluded_count} filtered out")
            
            if filtered_links:
                print("\n✅ Filtered links:")
                for i, link in enumerate(filtered_links, 1):
                    print(f"  {i}. {link}")
            else:
                print("ℹ️  All links were filtered out")
        else:
            print("ℹ️  No HTTPS links found in video description")
    else:
        error_message = result
        print(f"❌ Error: {error_message}")
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")
    
    # Show configuration
    print("\n⚙️  Bot Configuration:")
    print(f"  • YouTube API Key: {'*' * 20}{youtube_extractor.youtube.get_service_name()[-5:]}")
    print(f"  • Default filter words: {link_filter.get_user_filters(999)}")  # Default filters
    print(f"  • Bot supports all YouTube URL formats")
    
    return success

if __name__ == "__main__":
    try:
        test_youtube_extraction()
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        sys.exit(1)