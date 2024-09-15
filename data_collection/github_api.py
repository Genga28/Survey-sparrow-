import os
import pandas as pd
from github import Github, RateLimitExceededException

class GitHubDataCollector:
    def __init__(self):
        access_token = os.getenv('GITHUB_ACCESS_TOKEN')
        if not access_token:
            raise ValueError("GitHub Access Token is not set.")
        self.g = Github(access_token)
    
    def collect_data(self, repo_url):
        repo_name = repo_url.split('github.com/')[-1]
        repo = self.g.get_repo(repo_name)

        commits = []
        pull_requests = []
        issues = []
        reviews = []
       
        for commit in repo.get_commits():
            commits.append({
                "author": commit.author.login if commit.author else "Unknown",
                "date": commit.commit.author.date,
                "message": commit.commit.message,
                "sha": commit.sha
            })
            if len(commits) >= 100:  # Limit to 10 commits
                break

        for pr in repo.get_pulls(state='all'):
            pull_requests.append({
                "author": pr.user.login,
                "created_at": pr.created_at,
                "merged_at": pr.merged_at,
                "title": pr.title,
                "state": pr.state
            })
            if len(pull_requests) >= 100:  # Limit to 10 PRs
                break
        
        for issue in repo.get_issues(state='all'):
            issues.append({
                "author": issue.user.login,
                "created_at": issue.created_at,
                "closed_at": issue.closed_at,
                "title": issue.title,
                "state": issue.state,
                "labels": [label.name for label in issue.labels]
            })
            if len(issues) >= 100:  # Limit to 10 issues
                break
        
        for pr in repo.get_pulls(state='all'):
            for review in pr.get_reviews():
                reviews.append({
                    "pr_title": pr.title,
                    "reviewer": review.user.login,
                    "submitted_at": review.submitted_at,
                    "state": review.state,
                    "body": review.body
                })
                if len(reviews) >= 10:  # Limit to 10 reviews
                    break
            if len(reviews) >= 100:
                break

        print(f"Collected {len(commits)} commits")
        print(f"Collected {len(pull_requests)} pull requests")
        print(f"Collected {len(issues)} issues")
        print(f"Collected {len(reviews)} reviews")

        return commits, pull_requests, issues, reviews
    
    def save_data_to_csv(self, repo_url, commit_csv_path, pr_csv_path, issue_csv_path, review_csv_path):
        commits, pull_requests, issues, reviews = self.collect_data(repo_url)

        commit_df = pd.DataFrame(commits)
        pr_df = pd.DataFrame(pull_requests)
        issue_df = pd.DataFrame(issues)
        review_df = pd.DataFrame(reviews)

        if not commit_df.empty:
            commit_df.to_csv(commit_csv_path, index=False)
        else:
            print("No commits data to save.")

        if not pr_df.empty:
            pr_df.to_csv(pr_csv_path, index=False)
        else:
            print("No pull requests data to save.")

        if not issue_df.empty:
            issue_df.to_csv(issue_csv_path, index=False)
        else:
            print("No issues data to save.")

        if not review_df.empty:
            review_df.to_csv(review_csv_path, index=False)
        else:
            print("No reviews data to save.")

if __name__ == "__main__":
    collector = GitHubDataCollector()
    repo_url = "https://github.com/your-repo/your-project"  # Replace with your actual repo URL
    collector.save_data_to_csv(
        repo_url,
        'commits.csv',
        'pull_requests.csv',
        'issues.csv',
        'code_reviews.csv'
    )
