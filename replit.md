# YouTube Link Extractor Telegram Bot

## Overview

This is a Telegram bot that extracts HTTPS links from YouTube video descriptions. Users can send YouTube URLs to the bot, and it will fetch the video description using the YouTube Data API v3, extract all HTTPS links, and apply customizable filters to exclude unwanted domains.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a modular, object-oriented architecture with clear separation of concerns:

- **Bot Layer**: Handles Telegram interactions and user commands
- **Extraction Layer**: Manages YouTube API integration and video data retrieval
- **Filtering Layer**: Provides user-specific link filtering capabilities
- **Configuration Layer**: Centralizes all API keys and settings

The system is designed as a standalone Python application using asynchronous programming patterns for efficient handling of concurrent user requests.

## Key Components

### 1. Bot Module (`bot.py`)
- **Purpose**: Core Telegram bot functionality and user interaction handling
- **Key Features**: 
  - Command handlers for user interactions
  - YouTube URL validation using regex patterns
  - Integration with YouTube extractor and link filter components
- **Architecture Decision**: Uses python-telegram-bot library for robust Telegram API integration

### 2. YouTube Extractor (`youtube_extractor.py`)
- **Purpose**: YouTube video data retrieval and HTTPS link extraction
- **Key Features**:
  - YouTube video ID extraction from various URL formats
  - YouTube Data API v3 integration for description fetching
  - HTTPS link pattern matching and extraction
- **Architecture Decision**: Uses Google's official YouTube Data API client library for reliability and proper error handling

### 3. Link Filter (`link_filter.py`)
- **Purpose**: User-specific link filtering system
- **Key Features**:
  - Per-user filter word storage in memory
  - Default filter words with user customization
  - Case-insensitive filtering operations
- **Architecture Decision**: In-memory storage for simplicity; no persistent database required for this use case

### 4. Configuration (`config.py`)
- **Purpose**: Centralized configuration management
- **Contains**: API keys, tokens, default settings, and application constants
- **Architecture Decision**: Separate config file for easy deployment and credential management

### 5. Main Entry Point (`main.py`)
- **Purpose**: Application bootstrap and error handling
- **Key Features**:
  - Asynchronous bot initialization
  - Polling-based message handling
  - Comprehensive error logging

## Data Flow

1. **User Input**: User sends YouTube URL to Telegram bot
2. **URL Validation**: Bot validates YouTube URL format using regex
3. **Video ID Extraction**: YouTube extractor parses URL to extract video ID
4. **API Request**: YouTube Data API fetches video description
5. **Link Extraction**: Regex pattern extracts all HTTPS links from description
6. **Filter Application**: User-specific filters remove unwanted links
7. **Response**: Filtered links are sent back to user via Telegram

## External Dependencies

### APIs
- **Telegram Bot API**: For bot messaging and command handling
- **YouTube Data API v3**: For video description retrieval

### Python Libraries
- `python-telegram-bot`: Telegram bot framework
- `google-api-python-client`: YouTube API client
- `asyncio`: Asynchronous programming support
- Standard libraries: `re`, `logging`, `urllib.parse`

### Configuration Requirements
- Telegram Bot Token
- YouTube Data API Key
- Telegram API ID and Hash (for advanced features)

## Deployment Strategy

### Current Approach
- **Polling-based**: Bot uses polling instead of webhooks for simplicity
- **Single-process**: Runs as a standalone Python application
- **In-memory storage**: User preferences stored in application memory

### Scalability Considerations
- Stateless design allows for easy horizontal scaling
- In-memory storage limitation could be addressed with Redis or database for production
- Polling approach suitable for moderate traffic; webhooks recommended for high-volume usage

### Error Handling
- Comprehensive logging at INFO level
- Graceful handling of YouTube API errors
- User-friendly error messages for invalid URLs or API failures

### Host Configuration
- Configurable host and port settings (defaults to 0.0.0.0:8000)
- Environment suitable for containerization or cloud deployment