# ui/prompts.py
from rich.prompt import Confirm, Prompt
from typing import Dict


class UserPrompts:
    """
    Handles prompting the user for input.
    """

    def ask(self, prompt_text, **kwargs):
        """
        Prompts the user for input.

        Args:
            prompt_text (str): Text to display to the user
            **kwargs: Additional arguments for the prompt function

        Returns:
            str or bool: User input based on the type of the prompt
        """
        return Prompt.ask(prompt_text, **kwargs)

    def confirm(self, prompt_text):
        """
        Prompts the user for confirmation.

        Args:
            prompt_text (str): Text to display to the user for confirmation

        Returns:
            bool: True if user confirms, False otherwise
        """
        return Confirm.ask(prompt_text)

    def ask_for_filter_criteria(self) -> Dict[str, str]:
        """
        Prompts the user for filter criteria.

        Returns:
            dict: A dictionary containing filter criteria.
        """
        filters = {}

        if self.confirm("Do you want to filter users by minimum number of followers?"):
            filters["min_followers"] = self.ask(
                "Enter minimum number of followers")

        if self.confirm("Do you want to filter users by maximum number of followers?"):
            filters["max_followers"] = self.ask(
                "Enter maximum number of followers")

        if self.confirm("Do you want to filter users by minimum number of repositories?"):
            filters["min_repos"] = self.ask(
                "Enter minimum number of repositories")

        if self.confirm("Do you want to filter users by maximum number of repositories?"):
            filters["max_repos"] = self.ask(
                "Enter maximum number of repositories")

        return filters

    def ask_for_engagement_options(self) -> Dict[str, str]:
        """
        Prompts the user for automated engagement options.

        Returns:
           Dict: A dictionary with the engagement configuration.
        """
        options = {}

        options["star_repo"] = self.confirm(
            "Do you want to automatically star new repositories from your network?")
        options["like_commit"] = self.confirm(
            "Do you want to automatically like new commits from your network?")
        options["follow_back"] = self.confirm(
            "Do you want to automatically follow back the users that you are not following?")
        options["comment_issue_pr"] = self.confirm(
            "Do you want to comment on new issues and pull requests in your network?")
        if options["comment_issue_pr"]:
            options["comment_message"] = self.ask(
                "Please enter a comment message (default: 'Great job, keep up the amazing work! 😄')")

        return options
