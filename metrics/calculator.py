import pandas as pd
import os

METRICS_CSV_PATH = 'calculated_metrics.csv'

def calculate_metrics(commit_data, pr_data, issue_data):
    commit_df = pd.DataFrame(commit_data)
    pr_df = pd.DataFrame(pr_data)
    issue_df = pd.DataFrame(issue_data)

    if 'created_at' in issue_df.columns:
        issue_df['created_at'] = pd.to_datetime(issue_df['created_at'], errors='coerce')
    if 'closed_at' in issue_df.columns:
        issue_df['closed_at'] = pd.to_datetime(issue_df['closed_at'], errors='coerce')
    if 'merged_at' in pr_df.columns:
        pr_df['merged_at'] = pd.to_datetime(pr_df['merged_at'], errors='coerce')

    try:
        commit_frequency = commit_df.groupby("author").size().rename("commit_frequency")
    except KeyError:
        commit_frequency = pd.Series(name="commit_frequency")

    try:
        pr_merge_rate = pr_df[pr_df['merged_at'].notnull()].groupby('author').size() / pr_df.groupby('author').size()
        pr_merge_rate = pr_merge_rate.rename("pr_merge_rate")
    except (KeyError, ZeroDivisionError):
        pr_merge_rate = pd.Series(name="pr_merge_rate")

    try:
        issue_resolution_time = (issue_df['closed_at'] - issue_df['created_at']).dt.total_seconds().mean() / 3600
    except (KeyError, AttributeError):
        issue_resolution_time = float('nan')

    metrics = {
        'author': commit_frequency.index.tolist(),
        'commit_frequency': commit_frequency.values.tolist() if not commit_frequency.empty else [],
        'pr_merge_rate': pr_merge_rate.reindex(commit_frequency.index, fill_value=float('nan')).values.tolist() if not pr_merge_rate.empty else [],
        'avg_issue_resolution_time': [issue_resolution_time] * len(commit_frequency.index)
    }

    save_metrics_to_csv(metrics)

    return metrics

def save_metrics_to_csv(metrics):
    if os.path.exists(METRICS_CSV_PATH):
        existing_metrics = pd.read_csv(METRICS_CSV_PATH, index_col=0)
    else:
        existing_metrics = pd.DataFrame()

    metrics_df = pd.DataFrame(metrics)
    updated_df = pd.concat([existing_metrics, metrics_df]).drop_duplicates()
    updated_df.to_csv(METRICS_CSV_PATH, index=False)

def load_metrics_from_csv():
    if os.path.exists(METRICS_CSV_PATH):
        try:
            metrics_df = pd.read_csv(METRICS_CSV_PATH)
            metrics = {
                'commit_frequency': metrics_df.set_index('author')['commit_frequency'].to_dict() if 'commit_frequency' in metrics_df.columns else {},
                'pr_merge_rate': metrics_df.set_index('author')['pr_merge_rate'].to_dict() if 'pr_merge_rate' in metrics_df.columns else {},
                'avg_issue_resolution_time': metrics_df['avg_issue_resolution_time'].dropna().values[0] if 'avg_issue_resolution_time' in metrics_df.columns and not metrics_df['avg_issue_resolution_time'].dropna().empty else float('nan')
            }
            return metrics
        except Exception as e:
            print(f"Error loading metrics from CSV: {e}")
            return None
    else:
        return None
