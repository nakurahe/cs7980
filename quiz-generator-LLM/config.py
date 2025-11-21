"""
Configuration management for the Quiz Generator
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for API and application settings"""
    
    # Groq API Configuration
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
    
    # Baseline Generator API (for transcript-only quizzes)
    BASELINE_API_KEY = os.getenv('BASELINE_API_KEY')
    BASELINE_MODEL = os.getenv('BASELINE_MODEL', 'llama-3.3-70b-versatile')
    
    # File paths
    DATA_DIR = 'data'
    OUTPUT_DIR = 'output'
    
    # Quiz generation settings
    DEFAULT_NUM_QUESTIONS = 10
    DEFAULT_DIFFICULTY = 'medium'  # Changed to medium as default
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present"""
        if not cls.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY not found. Please set it in your .env file.\n"
                "Get your API key from https://console.groq.com"
            )
        if not cls.BASELINE_API_KEY:
            raise ValueError(
                "BASELINE_API_KEY not found. Please set it in your .env file.\n"
                "This is used for generating baseline (transcript-only) quizzes."
            )
        return True