import pandas as pd

def process_query(query, commits, pull_requests, issues, reviews, filtered_user=None):
    query = query.lower()

    if 'author' not in commits.columns or commits['author'].isnull().all():
        return ["No commit author data found."]

    if "commit frequency" in query:
        if filtered_user == 'All Users' or filtered_user is None:
            commit_frequency = commits['author'].value_counts()
            total_commits = commit_frequency.sum()
            response = [f"Total Commits across all users: {total_commits} commits"]
            response += [f"{author}: {count} commits" for author, count in commit_frequency.head().items()]
            return response
        else:
            user_commit_count = commits[commits['author'] == filtered_user]['author'].count()
            return [f"{filtered_user}: {user_commit_count} commits"]

    if "issue resolution time" in query:
        issues['created_at'] = pd.to_datetime(issues['created_at'])
        issues['closed_at'] = pd.to_datetime(issues['closed_at'])
        issues['resolution_time'] = (issues['closed_at'] - issues['created_at']).dt.total_seconds() / 3600
        avg_resolution_time = issues['resolution_time'].mean()
        return [f"Average Issue Resolution Time: {avg_resolution_time:.2f} hours"]

    if "code reviews" in query:
        review_counts = reviews['reviewer'].value_counts()
        response = [f"{reviewer}: {count}" for reviewer, count in review_counts.head().items()]
        return response

    return ["Couldn't understand Try different prompt"]
