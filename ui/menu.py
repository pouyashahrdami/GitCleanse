# ui/menu.py

from rich.console import Console
from rich.table import Table
from ui.prompts import UserPrompts


class Menu:
    """
    Handles displaying the main menu to the console.
    """

    def __init__(self, user_prompts: UserPrompts):
        """
        Initialize the menu with a console and a prompt handler.

        Args:
            user_prompts (UserPrompts): Prompt handler
        """
        self.console = Console()
        self.user_prompts = user_prompts

    def display(self) -> str:
        """
        Display the main menu and get user's choice.

        Returns:
            str: User's choice from the menu
        """
        # Create a table to display menu options
        table = Table(title="GitCleanse Menu",
                      show_header=True, header_style="bold blue")
        table.add_column("Option", justify="center", style="bold green")
        table.add_column("Action", style="bold")

        # Define the actions and their corresponding menu options
        table.add_row("1", "Analyze current relationships")
        table.add_row("2", "Unfollow non-followers")
        table.add_row("3", "Follow back your followers")
        table.add_row("4", "Discover and follow followers' followers")
        table.add_row("5", "Analyze user activity")
        table.add_row("6", "Display detailed user information")
        table.add_row("7", "Generate network report")
        table.add_row("8", "Display user dashboard")
        table.add_row("9", "Automated User Engagement")
        table.add_row("q", "Exit")

        # Print the menu table
        self.console.print(table)

        # Prompt for user choice
        choice = self.user_prompts.ask(
            "Choose an action",
            choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "q"],
            default="1"
        )
        return choice
