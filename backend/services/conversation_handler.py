"""
Conversation handler for natural interactions with the chatbot
"""

import re
from typing import Dict, Any, Optional
from enum import Enum


class ConversationType(Enum):
    GREETING = "greeting"
    MOVIE_QUERY = "movie_query"
    SMALL_TALK = "small_talk"
    GOODBYE = "goodbye"
    HELP = "help"
    UNKNOWN = "unknown"


class ConversationHandler:
    """Handles natural conversation patterns and responses"""
    
    def __init__(self):
        self.greeting_patterns = [
            r'\b(hi|hello|hey|good morning|good afternoon|good evening)\b',
            r'\b(how are you|how do you do|what\'s up|sup)\b',
            r'\b(nice to meet you|pleased to meet you)\b'
        ]
        
        self.goodbye_patterns = [
            r'\b(bye|goodbye|see you|farewell|take care)\b',
            r'\b(thanks|thank you|thx)\b.*\b(bye|goodbye)\b',
            r'\b(that\'s all|that\'s it|nothing else)\b'
        ]
        
        self.help_patterns = [
            r'\b(help|what can you do|what do you do|how do you work)\b',
            r'\b(show me|tell me|explain)\b.*\b(what|how|examples|commands|options|features)\b',
            r'\b(commands|options|features)\b'
        ]
        
        self.small_talk_patterns = [
            r'\b(how are you|how do you do|what\'s up)\b',
            r'\b(what\'s your name|who are you)\b',
            r'\b(what time|what day|what date)\b',
            r'\b(weather|temperature|rain|sunny)\b'
        ]
        
        self.movie_keywords = [
            'movie', 'movies', 'film', 'films', 'cinema', 'actor', 'actress', 
            'director', 'genre', 'rating', 'watch', 'watched', 'popular', 
            'best', 'top', 'recommend', 'find', 'show', 'list', 'search'
        ]
    
    def detect_conversation_type(self, message: str) -> ConversationType:
        """Detect the type of conversation from user message"""
        message_lower = message.lower().strip()
        
        # First, check for movie-related queries (highest priority)
        if any(keyword in message_lower for keyword in self.movie_keywords):
            return ConversationType.MOVIE_QUERY
        
        # Check for greetings
        for pattern in self.greeting_patterns:
            if re.search(pattern, message_lower):
                return ConversationType.GREETING
        
        # Check for goodbye
        for pattern in self.goodbye_patterns:
            if re.search(pattern, message_lower):
                return ConversationType.GOODBYE
        
        # Check for help requests (more specific patterns)
        for pattern in self.help_patterns:
            if re.search(pattern, message_lower):
                return ConversationType.HELP
        
        # Check for small talk
        for pattern in self.small_talk_patterns:
            if re.search(pattern, message_lower):
                return ConversationType.SMALL_TALK
        
        # If message is very short and doesn't contain movie keywords, treat as greeting
        if len(message.split()) <= 2 and not any(keyword in message_lower for keyword in self.movie_keywords):
            return ConversationType.GREETING
        
        return ConversationType.UNKNOWN
    
    def get_greeting_response(self, user_name: str = None) -> Dict[str, Any]:
        """Generate a friendly greeting response"""
        greetings = [
            f"Hello {user_name}! 👋 I'm your NQL Movie Chatbot. I can help you find and explore movies using natural language!",
            f"Hi there {user_name}! 🎬 Ready to discover some amazing movies? Just ask me anything about films!",
            f"Hey {user_name}! 🍿 Welcome to the movie world! I can help you find the perfect movie to watch.",
            f"Good to see you {user_name}! 🎭 I'm here to help you explore movies. What would you like to know?",
            f"Hello {user_name}! 🎪 I'm your movie assistant. Ask me about any movie, genre, actor, or director!"
        ]
        
        import random
        return {
            "type": "greeting",
            "message": random.choice(greetings),
            "suggestions": [
                "Find me the highest rated movies",
                "Show me action movies from 2024",
                "What are the most popular movies by Christopher Nolan?",
                "Find movies with rating above 8.0"
            ]
        }
    
    def get_help_response(self) -> Dict[str, Any]:
        """Generate a helpful response about capabilities"""
        return {
            "type": "help",
            "message": """🎬 **I'm your NQL Movie Chatbot!** Here's what I can help you with:

**🔍 Movie Queries:**
- Find movies by genre, director, or actor
- Search by rating, release date, or popularity
- Get recommendations based on your preferences

**💬 Natural Language:**
Just ask me naturally! For example:
- "Find me the most watched movies this year"
- "Show me the best action movies"
- "What are Christopher Nolan's highest rated films?"

**🎯 Example Questions:**
- "Find me the movies which was most watched between 01-01-2025 to 03-02-2025"
- "Show me the highest rated action movies"
- "What are the most popular movies by Christopher Nolan?"

**💡 Tips:**
- Be specific about what you're looking for
- You can combine multiple criteria
- Ask about trends, ratings, or comparisons

What would you like to explore? 🚀""",
            "suggestions": [
                "Find me the highest rated movies",
                "Show me action movies from 2024",
                "What are the most popular movies by Christopher Nolan?"
            ]
        }
    
    def get_small_talk_response(self, message: str) -> Dict[str, Any]:
        """Generate responses for small talk"""
        message_lower = message.lower()
        
        if re.search(r'\b(how are you|how do you do)\b', message_lower):
            return {
                "type": "small_talk",
                "message": "I'm doing great, thank you! 😊 I'm always excited to help you discover amazing movies. How can I assist you today?",
                "suggestions": [
                    "Find me some great movies to watch",
                    "Show me the highest rated films",
                    "What are the most popular movies?"
                ]
            }
        
        elif re.search(r'\b(what\'s your name|who are you)\b', message_lower):
            return {
                "type": "small_talk",
                "message": "I'm your NQL Movie Chatbot! 🎬 I specialize in helping you find and explore movies using natural language. I can understand complex queries about films, actors, directors, genres, and more!",
                "suggestions": [
                    "Show me what you can do",
                    "Find me some great movies",
                    "What are the most popular films?"
                ]
            }
        
        else:
            return {
                "type": "small_talk",
                "message": "That's interesting! 😊 I'm here to help you with all things movies. What would you like to know about films?",
                "suggestions": [
                    "Find me some great movies",
                    "Show me the highest rated films",
                    "What are the most popular movies?"
                ]
            }
    
    def get_goodbye_response(self, user_name: str = None) -> Dict[str, Any]:
        """Generate a friendly goodbye response"""
        goodbyes = [
            f"Goodbye {user_name}! 👋 Thanks for chatting about movies with me. Come back anytime!",
            f"See you later {user_name}! 🎬 Hope you found some great movies to watch!",
            f"Take care {user_name}! 🍿 Happy movie watching!",
            f"Farewell {user_name}! 🎭 Don't forget to check out those movie recommendations!",
            f"Bye {user_name}! 🎪 Thanks for using the NQL Movie Chatbot!"
        ]
        
        import random
        return {
            "type": "goodbye",
            "message": random.choice(goodbyes),
            "suggestions": []
        }
    
    def get_unknown_response(self, message: str) -> Dict[str, Any]:
        """Generate response for unclear messages"""
        return {
            "type": "unknown",
            "message": "I'm not sure I understand that. 🤔 I'm here to help you with movie-related queries! Try asking me about movies, actors, directors, genres, or ratings.",
            "suggestions": [
                "Find me some great movies",
                "Show me the highest rated films",
                "What are the most popular movies?",
                "Help me understand what you can do"
            ]
        }
    
    def process_message(self, message: str, user_name: str = None) -> Dict[str, Any]:
        """Process a user message and return appropriate response"""
        conversation_type = self.detect_conversation_type(message)
        
        if conversation_type == ConversationType.GREETING:
            return self.get_greeting_response(user_name)
        elif conversation_type == ConversationType.HELP:
            return self.get_help_response()
        elif conversation_type == ConversationType.SMALL_TALK:
            return self.get_small_talk_response(message)
        elif conversation_type == ConversationType.GOODBYE:
            return self.get_goodbye_response(user_name)
        elif conversation_type == ConversationType.MOVIE_QUERY:
            return {"type": "movie_query", "message": None}  # Let the main processor handle it
        else:
            return self.get_unknown_response(message)


# Global conversation handler instance
conversation_handler = ConversationHandler()
