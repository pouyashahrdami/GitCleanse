# core/models.py

from dataclasses import dataclass
from typing import List

@dataclass
class UserInfo:
    """Represents basic user information."""
    login: str
    name: str = None
    profile_url: str = None
    
@dataclass
class UserDetails:
    """Represents detailed user information."""
    username: str
    name: str
    followers: int
    following: int
    public_repos: int
    total_stars: int
    
@dataclass
class UserRecommendation:
    """Represents user recommendation data."""
    username: str
    mutual_connections: List[str]