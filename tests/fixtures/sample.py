"""
Sample Python file for testing ConfigSmith scanner.

This file demonstrates various patterns for accessing environment variables.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/db")

# API configuration
API_KEY = os.environ.get("API_KEY")  # Required, no default

# Application settings
DEBUG = os.getenv("DEBUG", "false")
PORT = int(os.getenv("PORT", "8000"))  # Type conversion

# Alternative access pattern
SECRET_KEY = os.environ["SECRET_KEY"]

# Cache settings
CACHE_TTL = int(os.environ.get("CACHE_TTL", "300"))
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
