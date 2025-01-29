# core/github_api.py

import requests
from typing import Dict, List
from time import sleep
from rich.console import Console

class GitHubAPIClient:
    """
    A client class to interact with the GitHub API.
    """
    def __init__(self, access_token: str):
        """
        Initialize the API client with an access token.
        
        Args:
            access_token (str): GitHub personal access token
        """
        self.headers = {
            'Authorization': f'token {access_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.base_url = 'https://api.github.com'
        self.console = Console()

    def get_user_info(self) -> dict:
        """
        Get authenticated user information.
        
        Returns:
            dict: User information from the GitHub API
        """
        response = requests.get(f'{self.base_url}/user', headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_user_details(self, username: str) -> dict:
        """
        Get detailed information about a user.
        
        Args:
            username (str): GitHub username
            
        Returns:
            dict: Detailed user information from the GitHub API
        """
        response = requests.get(
            f'{self.base_url}/users/{username}', headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_followers(self, username: str) -> Dict[str, dict]:
        """
        Get all followers of a user.
        
        Args:
            username (str): GitHub username
        
        Returns:
            Dict[str, dict]: Dictionary of follower usernames and their details
        """
        followers = {}
        page = 1

        with self.console.status("[bold green]Fetching followers..."):
            while True:
                response = requests.get(
                    f'{self.base_url}/users/{username}/followers',
                    headers=self.headers,
                    params={'page': page, 'per_page': 100}
                )
                response.raise_for_status()

                current_followers = response.json()
                if not current_followers:
                    break

                for user in current_followers:
                    followers[user['login']] = user
                page += 1
                sleep(1)  # Rate limiting precaution

        return followers

    def get_following(self, username: str) -> Dict[str, dict]:
        """
        Get all users a user is following.

        Args:
            username (str): GitHub username
        
        Returns:
            Dict[str, dict]: Dictionary of following usernames and their details
        """
        following = {}
        page = 1

        with self.console.status("[bold green]Fetching following..."):
            while True:
                response = requests.get(
                    f'{self.base_url}/users/{username}/following',
                    headers=self.headers,
                    params={'page': page, 'per_page': 100}
                )
                response.raise_for_status()

                current_following = response.json()
                if not current_following:
                    break

                for user in current_following:
                    following[user['login']] = user
                page += 1
                sleep(1)  # Rate limiting precaution

        return following

    def unfollow_user(self, username: str) -> bool:
        """
        Unfollow a specific user.
        
        Args:
            username (str): Username to unfollow
        
        Returns:
            bool: True if successful, False otherwise
        """
        response = requests.delete(
            f'{self.base_url}/user/following/{username}',
            headers=self.headers
        )
        return response.status_code == 204
    
    def follow_user(self, username: str) -> bool:
        """
        Follow a specific user.
        
        Args:
            username (str): Username to follow
        
        Returns:
            bool: True if successful, False otherwise
        """
        response = requests.put(
            f'{self.base_url}/user/following/{username}',
            headers=self.headers
        )
        return response.status_code == 204

    def get_user_followers_limited(self, username: str, max_pages: int = 3) -> Dict[str, dict]:
        """
        Get followers of a specific user up to a max number of pages.
        
        Args:
            username (str): GitHub username
            max_pages (int): Maximum number of pages to fetch (100 users per page)
            
        Returns:
            Dict[str, dict]: Dictionary of follower usernames and their details
        """
        followers = {}
        page = 1
        
        with self.console.status(f"[bold green]Fetching {username}'s followers..."):
            while page <= max_pages:
                response = requests.get(
                    f'{self.base_url}/users/{username}/followers',
                    headers=self.headers,
                    params={'page': page, 'per_page': 100}
                )
                response.raise_for_status()
                
                current_followers = response.json()
                if not current_followers:
                    break
                    
                for user in current_followers:
                    followers[user['login']] = user
                page += 1
                sleep(1)
                
        return followers
    
    def get_user_repos(self, username: str) -> List[dict]:
        """
        Get the list of repositories of a given user.
        
        Args:
            username (str): GitHub username
            
        Returns:
            List[dict]: List of repository details
        """
        response = requests.get(
            f'{self.base_url}/users/{username}/repos',
            headers=self.headers,
            params={'sort': 'updated', 'per_page': 100}
        )
        response.raise_for_status()
        return response.json()
    
    def get_user_events(self, username: str) -> List[dict]:
        """
        Get recent events for a user.
        
        Args:
            username (str): GitHub username
        
        Returns:
            List[dict]: List of recent event details.
        """
        response = requests.get(
            f'{self.base_url}/users/{username}/events',
            headers=self.headers,
            params={'per_page': 100}
        )
        response.raise_for_status()
        return response.json()
    
    def star_repository(self, owner: str, repo: str) -> bool:
        """
        Star a specific repository.
        
        Args:
            owner (str): Repository owner's username
            repo (str): Repository name
        
        Returns:
            bool: True if successful, False otherwise
        """
        response = requests.put(
            f'{self.base_url}/user/starred/{owner}/{repo}',
            headers=self.headers
        )
        return response.status_code == 204
    
    def create_comment(self, owner: str, repo: str, issue_number: int, comment: str) -> bool:
        """
        Create a comment on a specific issue or pull request.
        
        Args:
            owner (str): Repository owner's username
            repo (str): Repository name
            issue_number (int): Issue or pull request number
            comment (str): Comment to add
            
        Returns:
            bool: True if successful, False otherwise
        """
        response = requests.post(
            f'{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}/comments',
            headers=self.headers,
            json={'body': comment}
        )
        return response.status_code in [200, 201]
    
    def like_commit(self, owner: str, repo: str, commit_sha: str) -> bool:
        """
        Like a specific commit (by adding a reaction).
        
        Args:
            owner (str): Repository owner's username
            repo (str): Repository name
            commit_sha (str): Commit SHA
            
        Returns:
            bool: True if successful, False otherwise
        """
        response = requests.post(
           f"{self.base_url}/repos/{owner}/{repo}/commits/{commit_sha}/reactions",
           headers=self.headers,
           json={'content': '+1'}
        )
        return response.status_code == 201