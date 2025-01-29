# ui/console_display.py

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from typing import Dict, List
from core.github_api import GitHubAPIClient
from time import sleep
import requests
from datetime import datetime
from rich.layout import Layout
from rich.text import Text


class ConsoleDisplay:
    """
    Handles displaying data to the console.
    """

    def __init__(self):
        """Initialize the console display with the console object."""
        self.console = Console()

    def display_user_stats(self, mutual: dict, not_following_back: dict, not_followed_back: dict):
        """Display user statistics in a rich table format."""
        stats_table = Table(
            title="GitHub Relationship Statistics", show_header=True)
        stats_table.add_column("Category", style="cyan")
        stats_table.add_column("Count", style="magenta")

        stats_table.add_row("Mutual Followers", str(len(mutual)))
        stats_table.add_row("Not Following You Back",
                            str(len(not_following_back)))
        stats_table.add_row("You're Not Following Back",
                            str(len(not_followed_back)))

        self.console.print(stats_table)

    def display_users_table(self, users: Dict[str, dict], title: str, api_client: GitHubAPIClient):
        """Display user information in an enhanced table format."""
        if not users:
            return

        table = Table(
            title=title,
            show_header=True,
            border_style="blue",
            header_style="bold cyan",
            padding=(0, 2)
        )

        table.add_column("👤 Username", style="cyan")
        table.add_column("📛 Name", style="magenta")
        table.add_column("👥 Followers", style="green", justify="right")
        table.add_column("🔄 Following", style="blue", justify="right")
        table.add_column("📚 Repos", style="yellow", justify="right")
        table.add_column("⭐ Stars", style="cyan", justify="right")
        table.add_column("⏱️ Last Push", style="magenta", justify="right")

        with api_client.console.status("[bold green]Fetching user details"):
            for username, user in users.items():
                details = api_client.get_user_details(username)
                repos_response = requests.get(
                    f'{api_client.base_url}/users/{username}/repos',
                    headers=api_client.headers,
                    params={'per_page': 100}
                )
                total_stars = sum(repo['stargazers_count']
                                  for repo in repos_response.json())

                repos = api_client.get_user_repos(username)
                last_push_date = None
                if repos:
                    last_push_repo = max(
                        repos, key=lambda repo: datetime.fromisoformat(repo['updated_at'][:-1]))
                    last_push_date = datetime.fromisoformat(
                        last_push_repo['updated_at'][:-1]).strftime("%Y-%m-%d")

                table.add_row(
                    username,
                    details.get('name', 'N/A'),
                    str(details.get('followers', 0)),
                    str(details.get('following', 0)),
                    str(details.get('public_repos', 0)),
                    str(total_stars),
                    last_push_date if last_push_date else "N/A"
                )
                sleep(1)

        self.console.print(Panel(
            table,
            border_style="blue",
            padding=(1, 2)
        ))

    def display_user_activity_analysis(self, analysis: dict, username: str):
        """Display enhanced activity analysis with visual elements."""
        # Create layout for better organization

        layout = Layout()
        layout.split_column(
            Layout(name="header"),
            Layout(name="stats"),
            Layout(name="languages"),
            Layout(name="activity")
        )

        # Header
        created_date = datetime.strptime(
            analysis['created_at'], "%Y-%m-%dT%H:%M:%SZ")
        account_age = (datetime.now() - created_date).days

        header_content = Text()
        header_content.append(f"📊 Activity Analysis for ", style="bold blue")
        header_content.append(username, style="bold cyan")
        header_content.append(
            f"\nAccount age: {account_age} days", style="italic")
        if analysis['last_push_at']:
            header_content.append(
                f"\nLast push: {analysis['last_push_at'].strftime('%Y-%m-%d')}", style="italic")

        # Stats table
        stats_table = Table(show_header=False,
                            border_style="blue", padding=(0, 2))
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="magenta")

        stats_table.add_row("📚 Public Repositories",
                            str(analysis['public_repos']))
        stats_table.add_row("⭐ Total Stars", str(analysis['total_stars']))
        stats_table.add_row("🔄 Total Forks", str(analysis['total_forks']))
        stats_table.add_row("👥 Followers", str(analysis['followers']))
        stats_table.add_row("🔄 Following", str(analysis['following']))

        # Languages chart
        langs_table = Table(title="🔤 Top Languages",
                            show_header=True, border_style="blue")
        langs_table.add_column("Language", style="cyan")
        langs_table.add_column("Repos", style="magenta", justify="right")
        langs_table.add_column("Distribution", style="green")

        total_repos = sum(analysis['top_languages'].values())
        for lang, count in analysis['top_languages'].items():
            percentage = (count / total_repos) * 100
            bar = "█" * int(percentage / 5)
            langs_table.add_row(lang, str(count), bar)

        # Combine all elements
        self.console.print(Panel(header_content, border_style="blue"))
        self.console.print(
            Panel(stats_table, title="📈 Statistics", border_style="blue"))
        self.console.print(Panel(langs_table, border_style="blue"))

    def display_recommendation_table(self, recommended_users, api_client: GitHubAPIClient):
        """Display recommended users in a rich table format."""
        if not recommended_users:
            return

        table = Table(title="Recommended Users to Follow", show_header=True)
        table.add_column("Username", style="cyan")
        table.add_column("Mutual Connections", style="magenta")
        table.add_column("Followers", style="green")

        with api_client.console.status("[bold green]Fetching user details"):
            for username, mutual_connections in recommended_users:
                user_details = api_client.get_user_details(username)
                table.add_row(
                    username,
                    ", ".join(mutual_connections),
                    str(user_details.get('followers', 0))
                )
                sleep(0.5)

        self.console.print(table)

    def display_message(self, message, style=""):
        """Displays a message in the console with an optional style."""
        self.console.print(message, style=style)

    def display_panel(self, content, title="", border_style="blue"):
        """Displays content within a panel."""
        self.console.print(
            Panel(content, title=title, border_style=border_style))

    def display_mutual_relationships(self, mutual: Dict[str, dict], not_following_back: Dict[str, dict], not_followed_back: Dict[str, dict], api_client: GitHubAPIClient):
        """Display detailed mutual relationships with a better presentation."""
        self.console.print("[bold blue]Mutual Relationships[/bold blue]\n")

        if mutual:
            table = Table(
                title="Mutual Followers Details",
                show_header=True,
                border_style="blue",
                header_style="bold cyan",
                padding=(0, 2)
            )

            table.add_column("👤 Username", style="cyan")
            table.add_column("📛 Name", style="magenta")
            table.add_column("👥 Followers", style="green", justify="right")
            table.add_column("🔄 Following", style="blue", justify="right")
            table.add_column("📚 Repos", style="yellow", justify="right")
            table.add_column("⭐ Stars", style="cyan", justify="right")

            with api_client.console.status("[bold green]Fetching user details"):
                for username, user in mutual.items():
                    details = api_client.get_user_details(username)
                    repos_response = requests.get(
                        f'{api_client.base_url}/users/{username}/repos',
                        headers=api_client.headers,
                        params={'per_page': 100}
                    )
                    total_stars = sum(repo['stargazers_count']
                                      for repo in repos_response.json())

                    table.add_row(
                        username,
                        details.get('name', 'N/A'),
                        str(details.get('followers', 0)),
                        str(details.get('following', 0)),
                        str(details.get('public_repos', 0)),
                        str(total_stars)
                    )
                    sleep(0.5)
            self.console.print(
                Panel(table, border_style="blue", padding=(1, 2)))
        else:
            self.console.print("[yellow]No mutual followers found.[/yellow]")

        if not_following_back:
            self.console.print(
                "\n[bold blue]Users You Are Following That Don't Follow You Back:[/bold blue]\n")
            self.display_users_table(
                not_following_back, "Users Not Following You Back", api_client)
        else:
            self.console.print(
                "\n[green]You are following everyone who follows you.[/green]\n")

        if not_followed_back:
            self.console.print(
                "\n[bold blue]Users Following You That You Are Not Following Back:[/bold blue]\n")
            self.display_users_table(
                not_followed_back, "Users You Are Not Following Back", api_client)
        else:
            self.console.print(
                "[green]You are following everyone who follows you.[/green]\n")

    def display_dashboard(self, scored_users: Dict[str, dict], language_counts: Dict[str, int]):
        """Displays a dashboard with key metrics and insights."""
        layout = Layout()
        layout.split_column(
            Layout(name="user_scores", ratio=2),
            Layout(name="language_stats", ratio=1)
        )

        # User Scores Table
        user_score_table = Table(
            title="Top Users by Score", show_header=True, border_style="blue", padding=(0, 2))
        user_score_table.add_column("Username", style="cyan")
        user_score_table.add_column("Score", style="magenta", justify="right")
        user_score_table.add_column("Stars", style="green", justify="right")
        user_score_table.add_column("Forks", style="blue", justify="right")

        sorted_users = sorted(scored_users.items(
        ), key=lambda item: item[1]["score"], reverse=True)[:10]
        for username, data in sorted_users:
            user_score_table.add_row(
                username,
                str(data["score"]),
                str(sum(repo['stargazers_count'] for repo in data["repos"])),
                str(sum(repo['forks_count'] for repo in data["repos"]))

            )

        # Language Stats Table
        language_table = Table(title="Most Used Languages",
                               show_header=True, border_style="blue", padding=(0, 2))
        language_table.add_column("Language", style="cyan")
        language_table.add_column("Count", style="magenta", justify="right")

        for language, count in list(language_counts.items())[:5]:
            language_table.add_row(language, str(count))

        layout["user_scores"].update(
            Panel(user_score_table, border_style="blue"))
        layout["language_stats"].update(
            Panel(language_table, border_style="blue"))

        self.console.print(layout)

    def display_engagement_results(self, performed_actions: Dict[str, List[str]]):
        """Displays the results of the automated engagements"""
        self.console.print(
            "\n[bold blue]Automated User Engagement Results:[/bold blue]\n")

        for username, actions in performed_actions.items():
            if actions:
                self.console.print(f"[bold cyan]User: {username}[/bold cyan]")
                for action in actions:
                    self.console.print(f"- {action}")
            else:
                self.console.print(f"[cyan]No actions for user: {
                                   username}[/cyan]")
