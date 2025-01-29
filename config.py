"""Configuration settings for the application."""

import os
from rich.prompt import Prompt
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()


def get_github_token():
    """
    Retrieves the GitHub token from environment variables or user input.

    Returns:
        str: GitHub personal access token
    """
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        token = Prompt.ask("Enter your GitHub token", password=True)
    return token
