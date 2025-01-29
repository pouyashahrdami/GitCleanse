# reports/report_generator.py

from typing import List

def save_report(unfollowed: List[str], timestamp: str):
    """Save unfollowed users to a report file."""
    filename = f"github_unfollow_report_{timestamp}.txt"
    with open(filename, 'w') as f:
        f.write(f"GitHub Unfollow Report - {timestamp}\n")
        f.write("-" * 50 + "\n")
        f.write(f"Total users unfollowed: {len(unfollowed)}\n\n")
        if unfollowed:
            f.write("Unfollowed users:\n")
            for user in unfollowed:
                f.write(f"- {user}\n")
    return filename