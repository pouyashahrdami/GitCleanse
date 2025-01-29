#  _______ __________________ _______  _        _______  _______  _        _______  _______
# (  ____ \\__   __/\__   __/(  ____ \( \      (  ____ \(  ___  )( (    /|(  ____ \(  ____ \
# | (    \/   ) (      ) (   | (    \/| (      | (    \/| (   ) ||  \  ( || (    \/| (    \/
# | |         | |      | |   | |      | |      | (__    | (___) ||   \ | || (_____ | (__
# | | ____    | |      | |   | |      | |      |  __)   |  ___  || (\ \) |(_____  )|  __)
# | | \_  )   | |      | |   | |      | |      | (      | (   ) || | \   |      ) || (
# | (___) |___) (___   | |   | (____/\| (____/\| (____/\| )   ( || )  \  |/\____) || (____/\
# (_______)\_______/   )_(   (_______/(_______/(_______/|/     \||/    )_)\_______)(_______/
# ---------------------- By Pouya
# main.py
from core.github_api import GitHubAPIClient
from core.utils import GitHubFollowerAnalyzer
from ui.console_display import ConsoleDisplay
from ui.menu import Menu
from ui.prompts import UserPrompts
from config import get_github_token
import requests


def main():
    """Main function to execute the GitHub follower manager."""
    display = ConsoleDisplay()  # Initialize console display handler
    user_prompts = UserPrompts()  # Initialize user prompts handler

    # Welcome message
    display.display_panel(
        "[bold blue]GitCleanse GitHub Follower Manager[/bold blue]\n"
        "[italic]Analyze and manage your GitHub relationships[/italic]"
    )

    # Get GitHub token
    token = get_github_token()  # Retrieve the GitHub access token

    try:
        # Initialize core components
        api_client = GitHubAPIClient(token)  # API client
        # Analyzer for followers/following
        analyzer = GitHubFollowerAnalyzer(api_client)
        menu = Menu(user_prompts)  # Menu handler
        user_info = api_client.get_user_info()  # Get current user info

        # Greet the user
        display.display_message(
            f"\n[bold green]Welcome, {user_info['name'] or user_info['login']}![/bold green]")
        display.display_message(
            f"[italic]Profile: https://github.com/{user_info['login']}[/italic]\n")

        while True:
            # Show the menu and get the user's choice
            choice = menu.display()  # Display the menu and get user's selection

            if choice == "q":  # If user chooses to exit
                display.display_message(
                    "[yellow]Exiting the GitCleanse. Goodbye![/yellow]")
                break

            # Map choices to actions (using lambda to avoid early execution)
            actions = {
                # Analyze relations
                "1": ("Analyze current relationships", analyzer.analyze_followers),
                # Unfollow
                "2": ("Unfollow non-followers", lambda: cleanup_following(analyzer, display, user_prompts)),
                # Follow back
                "3": ("Follow back your followers", lambda: follow_my_followers(analyzer, display, user_prompts)),
                "4": ("Discover and follow followers' followers",
                      lambda: discover_and_follow_followers_followers(analyzer, display, api_client, user_prompts)),
                "5": ("Analyze user activity",
                      # Display user activity
                      lambda: display_user_activity(analyzer, api_client, display, user_prompts)),
                "6": ("Display detailed user information",
                      lambda: display.display_users_table(
                          {user_info['login']: user_info},
                          "Your Profile Details", api_client
                      )),  # Display detailed info
                # Do nothing for now
                "7": ("Generate network report", lambda: display.display_message("[yellow]Report generation is not yet implemented[/yellow]")),
                # Display Dashboard
                "8": ("Display user dashboard", lambda: display_dashboard(analyzer, display)),
                # Automated Engagement
                "9": ("Automated User Engagement", lambda: automated_user_engagement(analyzer, display, user_prompts))
            }

            action_tuple = actions.get(choice)  # Get the action tuple
            if action_tuple:
                action_name, action_func = action_tuple  # unpack if found
                display.display_message(
                    f"\n[bold blue]--- {action_name} ---[/bold blue]\n")
                try:
                    result = action_func() if action_func else None  # Execute the chosen function

                    # Handle specific actions with additional prompts
                    if choice == "1":  # Analyze relationships
                        mutual, not_following_back, not_followed_back = result
                        display.display_user_stats(
                            mutual, not_following_back, not_followed_back)

                        if not_following_back:
                            if user_prompts.confirm("Do you want to see the list of users not following you back?"):
                                filtered_users = filter_users(
                                    analyzer, user_prompts, not_following_back)
                                display.display_users_table(
                                    filtered_users, "Users Not Following You Back", api_client)

                        if not_followed_back:
                            if user_prompts.confirm("Do you want to see the list of users you're not following back?"):
                                filtered_users = filter_users(
                                    analyzer, user_prompts, not_followed_back)
                                display.display_users_table(
                                    filtered_users, "Users You're Not Following Back", api_client)

                except requests.exceptions.RequestException as e:
                    display.display_message(
                        f"[bold red]An API error occurred:[/bold red] {str(e)}", style="red")
                except Exception as e:
                    display.display_message(
                        f"[bold red]Error during operation:[/bold red] {str(e)}", style="red")
            else:
                display.display_message("[red]Invalid menu choice[/red]")

            display.display_message("\n" + "-" * 50 + "\n")  # Separator

    except requests.exceptions.RequestException as e:
        display.display_message(
            f"[bold red]An error occurred:[/bold red] {str(e)}", style="red")
    except KeyboardInterrupt:
        display.display_message(
            "\n[yellow]Operation cancelled by user.[/yellow]")


def cleanup_following(analyzer: GitHubFollowerAnalyzer, display: ConsoleDisplay, user_prompts: UserPrompts):
    """Handles the cleanup following action."""
    mutual, not_following_back, not_followed_back = analyzer.analyze_followers(
    )  # Get analysis results
    display.display_user_stats(
        mutual, not_following_back, not_followed_back)  # Display stats

    if not not_following_back:  # If everyone follows back
        display.display_message(
            "[green]Everyone you follow is following you back! No action needed.[/green]")
        return []

    display.display_message(f"\n[yellow]Found {len(
        not_following_back)} users who don't follow you back:[/yellow]")

    # Ask for confirmation
    if not user_prompts.confirm("\nDo you want to proceed with unfollowing these users?"):
        display.display_message(
            "[yellow]Operation cancelled by user.[/yellow]")
        return []

    unfollowed_users = []
    for username in analyzer.create_progress_bar("Unfollowing users...").track(not_following_back.keys()):
        # Unfollow user via API
        if analyzer.api_client.unfollow_user(username):
            unfollowed_users.append(username)  # Collect the user

    if unfollowed_users:  # Confirmation message
        display.display_message(f"[green]Successfully unfollowed {
                                len(unfollowed_users)} users.[/green]")
        # Display list prompt
        if user_prompts.confirm("Do you want to see the list of unfollowed users?"):
            display.display_panel(
                "\n".join(unfollowed_users), title="Unfollowed Users", border_style="blue")
    else:
        display.display_message("[yellow]No users were unfollowed.[/yellow]")
    return unfollowed_users


def follow_my_followers(analyzer: GitHubFollowerAnalyzer, display: ConsoleDisplay, user_prompts: UserPrompts):
    """Handles following back users."""
    _, _, not_followed_back = analyzer.analyze_followers(
    )  # Get followers not followed by you
    newly_followed = []

    if not not_followed_back:  # If already following all followers
        display.display_message(
            "[green]You're already following all your followers![/green]")
        return []

    display.display_message(f"\n[yellow]Found {len(
        not_followed_back)} followers you're not following back:[/yellow]")
    display.display_users_table(
        not_followed_back, "Users You Could Follow Back", analyzer.api_client)  # Display the list

    # Confirmation prompt
    if not user_prompts.confirm("\nDo you want to follow these users back?"):
        display.display_message(
            "[yellow]Operation cancelled by user.[/yellow]")
        return []

    for username in analyzer.create_progress_bar("Following users...").track(not_followed_back.keys()):
        if analyzer.api_client.follow_user(username):  # Follow user via API
            newly_followed.append(username)  # Collect followed users

    if newly_followed:  # Confirmation message
        display.display_message(f"[green]Successfully followed back {
                                len(newly_followed)} users.[/green]")
        # Display list prompt
        if user_prompts.confirm("Do you want to see the list of followed users?"):
            display.display_panel("\n".join(newly_followed),
                                  title="Followed Users", border_style="blue")
    else:
        display.display_message(
            "[yellow]No users were followed back.[/yellow]")

    return newly_followed


def discover_and_follow_followers_followers(analyzer: GitHubFollowerAnalyzer, display: ConsoleDisplay, api_client: GitHubAPIClient, user_prompts: UserPrompts):
    """Handles the discovery and follow feature."""
    max_users = int(user_prompts.ask(
        "Enter maximum number of users to follow", default="50"))
    newly_followed, recommended_users = analyzer.follow_followers_followers(
        max_users)  # Find recommended users

    if not recommended_users:  # If no recommendations
        display.display_message(
            "[yellow]No new potential connections found.[/yellow]")
        return []

    display.display_recommendation_table(
        recommended_users, api_client)  # Display the recommendation list

    # Confirmation
    if user_prompts.confirm("\nDo you want to follow these recommended users?"):
        if newly_followed:
            display.display_message(f"[green]Successfully followed {
                                    len(newly_followed)} new users.[/green]")
            # Display list
            if user_prompts.confirm("Do you want to see the list of newly followed users?"):
                display.display_panel(
                    "\n".join(newly_followed), title="Newly Followed Users", border_style="blue")
        else:
            display.display_message(
                "[yellow]No new users were followed.[/yellow]")

    return newly_followed


def display_user_activity(analyzer: GitHubFollowerAnalyzer, api_client: GitHubAPIClient, display: ConsoleDisplay, user_prompts: UserPrompts):
    """Handles displaying user activity analysis."""
    username = user_prompts.ask("Enter username to analyze")  # Get username
    with analyzer.create_progress_bar(f"Analyzing {username}'s activity") as progress:
        task = progress.add_task("Processing...", total=100)
        analysis = analyzer.analyze_user_activity(username)  # Analyze activity
        progress.update(task, completed=100)
    display.display_user_activity_analysis(
        analysis, username)  # Display the results


def filter_users(analyzer: GitHubFollowerAnalyzer, user_prompts: UserPrompts, users: dict):
    """Handles filtering users based on criteria."""
    filter_criteria = user_prompts.ask_for_filter_criteria()
    filtered_users = analyzer.filter_users(users, filter_criteria)
    return filtered_users


def display_dashboard(analyzer: GitHubFollowerAnalyzer, display: ConsoleDisplay):
    """Handles displaying the user dashboard."""
    user_info = analyzer.api_client.get_user_info()
    followers = analyzer.api_client.get_followers(user_info["login"])
    scored_users = analyzer.calculate_user_scores(followers)
    language_counts = analyzer.analyze_network_languages(followers)
    display.display_dashboard(scored_users, language_counts)


def automated_user_engagement(analyzer: GitHubFollowerAnalyzer, display: ConsoleDisplay, user_prompts: UserPrompts):
    """Handles automated user engagements."""
    user_info = analyzer.api_client.get_user_info()
    followers = analyzer.api_client.get_followers(user_info["login"])
    engagement_config = user_prompts.ask_for_engagement_options()
    performed_actions = analyzer.perform_automated_engagements(
        followers, engagement_config)
    display.display_engagement_results(performed_actions)


if __name__ == "__main__":
    main()
