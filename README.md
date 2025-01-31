![GitCleanse](https://github.com/pouyashahrdami/GitCleanse/raw/main/banner.jpg)

# GitCleanse Enhanced GitHub Follower Manager

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

This is the most powerful command-line tool designed to help you manage and grow your GitHub network effectively. It provides advanced analysis, cleanup, and discovery features, as well as automated engagement capabilities.

## Features

-   **Relationship Analysis:** Analyze your followers, following, and mutual relationships.
-   **Unfollow Non-Followers:** Unfollow users who are not following you back.
-   **Follow Back Followers:** Follow back users who are following you but you're not following back.
-   **Discover New Connections:** Discover and follow the followers of your followers.
-   **User Activity Analysis:** Analyze user profiles and activity, including repository details, stars, and last push.
-   **User Filtering:** Filter users based on criteria like follower count or repository count.
-   **User Scoring:** Score users based on their activity and contributions.
-   **Network Language Analysis:** Analyze the most used languages in your network's repositories.
-   **Customizable Dashboard:** Display a dashboard of key network metrics, top users, and language stats.
-   **Automated User Engagement:** Automatically star new repositories, like new commits, comment on issues and pull requests, and follow back users that follow you.
-   **GitHub API:** Uses the official GitHub API to interact with your profile.
-   **Rich Console:** Utilizes the `rich` library for beautiful and interactive console output.

## Demos
![GitCleanse_demo1](https://github.com/pouyashahrdami/GitCleanse/raw/main/demo1.png)
-
![GitCleanse_demo2](https://github.com/pouyashahrdami/GitCleanse/raw/main/demo2.png)
-
![GitCleanse_demo3](https://github.com/pouyashahrdami/GitCleanse/raw/main/demo3.png)
-
![GitCleanse_demo3](https://github.com/pouyashahrdami/GitCleanse/raw/main/demo4.png)
-
and more... just give a try and you will love it :)

## Prerequisites

Before using the application, ensure you have:

-   **Python 3.8 or higher:** [Download Python](https://www.python.org/downloads/)
-   **GitHub Personal Access Token:**
    -   You can generate a token by going to your [GitHub settings](https://github.com/settings/tokens).
    -   The token needs the `repo` or `public_repo` scope (depending on whether you need to access private repos).

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/pouyashahrdami/GitCleanse.git
    cd your-repository
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    (Ensure you create a `requirements.txt` file which includes all the libraries, in your case `rich` and `requests`)

## Usage

1.  **Set your GitHub token:**

    -   **Environment Variable:** Recommended method. Set the `GITHUB_TOKEN` environment variable to your personal access token.
      -   **Linux/macOS:** `export GITHUB_TOKEN=your_token`
      -   **Windows (cmd.exe):** `set GITHUB_TOKEN=your_token`
      -   **Windows (PowerShell):** `$env:GITHUB_TOKEN = "your_token"`
    -   **Direct Input:** If the environment variable is not set, the application will prompt you to enter your token at the start.
2.  **Run the application:**
    ```bash
    python main.py
    ```
3.  **Follow the on-screen menu:**
    The application will present a menu with the available actions. Enter the corresponding number to perform a specific task.

## Menu Options

-   **1:** Analyze current relationships (mutual followers, non-followers, etc.).
-   **2:** Unfollow non-followers (users who don't follow you back).
-   **3:** Follow back your followers (users who follow you but you don't follow back).
-   **4:** Discover and follow followers' followers (with a user-defined limit).
-   **5:** Analyze user activity (show details about user contributions).
-   **6:** Display detailed user information (about the current user).
-   **7:** Generate network report (not yet implemented).
-   **8:** Display user dashboard (key metrics and insights).
-   **9:** Automated User Engagement (configure and perform automated actions).
-   **q:** Exit the application.

## Automated User Engagement Details
The Automated User Engagement feature allows you to configure the following actions:

-   **Star New Repositories:** Automatically star new repositories created by users in your network.
-   **Like New Commits:** Automatically like (add +1 reaction to) new commits made by users in your network.
-   **Comment on Issues/PRs:** Automatically comment on newly opened issues or pull requests in your network using a customizable message.
-   **Follow Back Users:** Automatically follow back users in your network that you're not following.
-   **Rate Limiting:** All actions respect GitHub's rate limits with sleeps between API requests.

## Configuration

-   The application reads the GitHub token from the `GITHUB_TOKEN` environment variable.
- You can configure various aspects of the application via the on-screen prompts including:
   - Filter users by minimum or maximum number of followers or repositories.
   - Set the maximum number of users to follow in the `Discover and Follow Followers' Followers` option.
   - Enable or disable automated engagements.
   - Set the comment message when commenting on issues or pull requests.
-   You can provide a default value to the `ask` function in `ui/prompts.py` if you would like to make it easier to use the application.

## Contributing

Contributions are welcome! Please feel free to fork the repository, make changes, and submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This application interacts with the GitHub API, and you should use it responsibly and respect GitHub's rate limits. Misuse of this application can lead to API rate limit issues and potential account suspension.