# core/utils.py

from typing import Dict, Tuple, List
from core.github_api import GitHubAPIClient
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from time import sleep
from datetime import datetime
import random


class GitHubFollowerAnalyzer:
    """
    Analyzes follower and following relationships.
    """

    def __init__(self, api_client: GitHubAPIClient):
        """
        Initialize the analyzer with a GitHub API client.

        Args:
            api_client (GitHubAPIClient): An instance of the GitHub API client
        """
        self.api_client = api_client
        self.console = Console()

    def analyze_followers(self) -> Tuple[Dict[str, dict], Dict[str, dict], Dict[str, dict]]:
        """
        Analyze followers and following lists.

        Returns:
            Tuple containing:
            - Dict of mutual followers
            - Dict of non-following users
            - Dict of non-followers being followed
        """
        user_info = self.api_client.get_user_info()
        username = user_info['login']

        followers = self.api_client.get_followers(username)
        following = self.api_client.get_following(username)

        follower_usernames = set(followers.keys())
        following_usernames = set(following.keys())

        mutual = {username: following[username]
                  for username in follower_usernames & following_usernames}
        not_following_back = {username: following[username]
                              for username in following_usernames - follower_usernames}
        not_followed_back = {username: followers[username]
                             for username in follower_usernames - following_usernames}

        return mutual, not_following_back, not_followed_back

    def create_progress_bar(self, description: str) -> Progress:
        """Create a customized progress bar."""
        return Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(complete_style="green", finished_style="green"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=self.console
        )

    def follow_followers_followers(self, max_users: int = 50) -> Tuple[list, list]:
        """
        Follow your followers' followers (network expansion).

        Args:
            max_users (int): Maximum number of new users to follow

        Returns:
            Tuple: List of newly followed users and list of recommended users
        """
        my_followers = self.api_client.get_followers(
            self.api_client.get_user_info()['login'])
        following = self.api_client.get_following(
            self.api_client.get_user_info()['login'])
        newly_followed = []
        potential_follows = {}

        with self.console.status("[bold green]Analyzing network..."):
            for follower in my_followers.keys():
                # Get this follower's followers
                followers_followers = self.api_client.get_user_followers_limited(
                    follower)
                for username, user_data in followers_followers.items():
                    if username not in following and username not in my_followers:
                        if username not in potential_follows:
                            potential_follows[username] = {
                                'data': user_data,
                                'recommended_by': [follower]
                            }
                        else:
                            potential_follows[username]['recommended_by'].append(
                                follower)

        # Sort by number of mutual connections
        sorted_potentials = sorted(
            potential_follows.items(),
            key=lambda x: len(x[1]['recommended_by']),
            reverse=True
        )

        if not sorted_potentials:
            return [], []

        recommended_users = [
            (username, data['recommended_by']) for username, data in sorted_potentials[:max_users]
        ]

        for username, _ in sorted_potentials[:max_users]:
            if self.api_client.follow_user(username):
                newly_followed.append(username)
                sleep(1)

        return newly_followed, recommended_users

    def analyze_user_activity(self, username: str) -> dict:
        """
        Analyze a user's GitHub activity and profile.

        Args:
            username (str): GitHub username to analyze

        Returns:
            dict: Activity analysis results
        """
        user_details = self.api_client.get_user_details(username)

        # Get user's repositories
        repos = self.api_client.get_user_repos(username)

        # Calculate activity metrics
        total_stars = sum(repo['stargazers_count'] for repo in repos)
        total_forks = sum(repo['forks_count'] for repo in repos)
        languages = {}
        for repo in repos:
            if repo['language']:
                languages[repo['language']] = languages.get(
                    repo['language'], 0) + 1

        last_push = None
        if repos:
            last_push_repo = max(
                repos, key=lambda repo: datetime.fromisoformat(repo['updated_at'][:-1]))
            last_push = datetime.fromisoformat(
                last_push_repo['updated_at'][:-1])

        return {
            'public_repos': user_details['public_repos'],
            'followers': user_details['followers'],
            'following': user_details['following'],
            'total_stars': total_stars,
            'total_forks': total_forks,
            'top_languages': dict(sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]),
            'created_at': user_details['created_at'],
            'updated_at': user_details['updated_at'],
            'last_push_at': last_push
        }

    def filter_users(self, users: Dict[str, dict], criteria: dict) -> Dict[str, dict]:
        """
        Filters users based on specified criteria.

        Args:
            users (Dict[str, dict]): A dictionary of user details
            criteria (dict): Filtering criteria

        Returns:
            Dict[str, dict]: A dictionary of filtered users
        """
        filtered_users = users.copy()

        if not criteria:
            return filtered_users

        with self.console.status("[bold green]Filtering users..."):

            for key, value in criteria.items():

                if key == "min_followers":
                    filtered_users = {
                        user: details
                        for user, details in filtered_users.items()
                        if self.api_client.get_user_details(user).get('followers', 0) >= int(value)
                    }

                elif key == "max_followers":
                    filtered_users = {
                        user: details
                        for user, details in filtered_users.items()
                        if self.api_client.get_user_details(user).get('followers', 0) <= int(value)
                    }

                elif key == "min_repos":
                    filtered_users = {
                        user: details
                        for user, details in filtered_users.items()
                        if self.api_client.get_user_details(user).get('public_repos', 0) >= int(value)
                    }

                elif key == "max_repos":
                    filtered_users = {
                        user: details
                        for user, details in filtered_users.items()
                        if self.api_client.get_user_details(user).get('public_repos', 0) <= int(value)
                    }

            return filtered_users

    def calculate_user_scores(self, users: Dict[str, dict]) -> Dict[str, dict]:
        """
        Calculates scores for users based on their activity and contributions.

        Args:
            users (Dict[str, dict]): A dictionary of user details.

        Returns:
            Dict[str, dict]: A dictionary containing user scores and details.
        """
        scored_users = {}
        with self.console.status("[bold green]Calculating user scores..."):
            for username in users:
                details = self.api_client.get_user_details(username)
                repos = self.api_client.get_user_repos(username)
                total_stars = sum(repo['stargazers_count'] for repo in repos)
                total_forks = sum(repo['forks_count'] for repo in repos)

                activity_score = 0
                if repos:
                    last_push_repo = max(
                        repos, key=lambda repo: datetime.fromisoformat(repo['updated_at'][:-1]))
                    last_push = datetime.fromisoformat(
                        last_push_repo['updated_at'][:-1])
                    activity_score = (datetime.now() - last_push).days

                # User score calculation is a simple sum of starts, forks, and the inverted activity score
                user_score = total_stars + total_forks - \
                    activity_score if activity_score else total_stars + total_forks
                scored_users[username] = {
                    "score": user_score,
                    "details": details,
                    "repos": repos
                }
        return scored_users

    def analyze_network_languages(self, users: Dict[str, dict]) -> Dict[str, int]:
        """
        Analyzes the most used languages in a network of users.

        Args:
            users (Dict[str, dict]): A dictionary of user details.

        Returns:
            Dict[str, int]: A dictionary with language counts.
        """
        language_counts = {}
        with self.console.status("[bold green]Analyzing network languages..."):
            for username in users:
                repos = self.api_client.get_user_repos(username)
                for repo in repos:
                    if repo.get('language'):
                        language_counts[repo['language']] = language_counts.get(
                            repo['language'], 0) + 1

        return dict(sorted(language_counts.items(), key=lambda item: item[1], reverse=True))

    def perform_automated_engagements(self, users: Dict[str, dict], config: dict) -> Dict[str, List[str]]:
        """
        Performs automated engagements on the given users.

        Args:
           users (Dict[str, dict]): Dictionary of users to engage with
           config (dict): Dictionary of configuration for the actions.

        Returns:
           Dict[str, List[str]]: Dictionary of users with the performed actions.
        """
        performed_actions = {}

        with self.create_progress_bar("Performing automated engagements...") as progress:
            task = progress.add_task("Engaging users...", total=len(users))

            for username in users:
                user_actions = []
                events = self.api_client.get_user_events(username)

                for event in events:
                    if event["type"] == "CreateEvent":
                        if config.get("star_repo", False):
                            repo_owner = event["repo"]["name"].split("/")[0]
                            repo_name = event["repo"]["name"].split("/")[1]
                            if self.api_client.star_repository(repo_owner, repo_name):
                                user_actions.append(
                                    f"Starred repo: {event['repo']['name']}")
                                # Respect rate limits
                                sleep(random.uniform(0.5, 2))

                    elif event["type"] == "PushEvent":
                        if config.get("like_commit", False):
                            for commit in event["payload"].get("commits", []):
                                repo_owner = event["repo"]["name"].split(
                                    "/")[0]
                                repo_name = event["repo"]["name"].split("/")[1]
                                commit_sha = commit.get("sha")
                                if commit_sha and self.api_client.like_commit(repo_owner, repo_name, commit_sha):
                                    user_actions.append(
                                        f"Liked commit: {commit_sha}")
                                    # Respect rate limits
                                    sleep(random.uniform(0.5, 2))

                    elif event["type"] in ["IssuesEvent", "PullRequestEvent"]:
                        if config.get("comment_issue_pr", False) and event["payload"].get("action", "") in ["opened", "created", "submitted"]:
                            comment_text = config.get(
                                "comment_message", "Great job, keep up the amazing work! 😄")
                            repo_owner = event["repo"]["name"].split("/")[0]
                            repo_name = event["repo"]["name"].split("/")[1]
                            issue_number = event["payload"]["issue"]["number"] if event[
                                "type"] == "IssuesEvent" else event["payload"]["pull_request"]["number"]
                            if self.api_client.create_comment(repo_owner, repo_name, issue_number, comment_text):
                                user_actions.append(f"Commented on {
                                                    'issue' if event['type'] == 'IssuesEvent' else 'PR'} {issue_number}")
                                # Respect rate limits
                                sleep(random.uniform(0.5, 2))

                if config.get("follow_back", False):
                    if username not in self.api_client.get_following(self.api_client.get_user_info()["login"]):
                        if self.api_client.follow_user(username):
                            user_actions.append(f"Followed user back")
                            # Respect rate limits
                            sleep(random.uniform(0.5, 2))

                performed_actions[username] = user_actions
                progress.update(task, advance=1)

        return performed_actions
