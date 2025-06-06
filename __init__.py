"""
Multi-Agent Conversation System

A system for managing conversations between AI agents with different roles
and capabilities, including file management and image generation.
"""

from .agents import Agent
from .image_generator import ImageGenerator
from .file_manager import FileManager
from .conversation_manager import ConversationManager

__version__ = "1.0.0"
__all__ = ["Agent", "ImageGenerator", "FileManager", "ConversationManager"]
