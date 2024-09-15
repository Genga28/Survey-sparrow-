import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def generate_charts(commits_df, issues_df, pull_request_df, user_selected=False):
    commits_df['date'] = pd.to_datetime(commits_df['date'])
    commits_df['hour'] = commits_df['date'].dt.hour
    commits_df['day_of_week'] = commits_df['date'].dt.day_name()
    commits_by_day_hour = commits_df.groupby(['day_of_week', 'hour']).size().reset_index(name='commit_count')

    issues_df['created_at'] = pd.to_datetime(issues_df['created_at'])
    issues_df['closed_at'] = pd.to_datetime(issues_df['closed_at'])
    issues_df['resolution_time'] = (issues_df['closed_at'] - issues_df['created_at']).dt.total_seconds() / 3600

    pull_request_df['created_at'] = pd.to_datetime(pull_request_df['created_at'])
    pull_request_df['merged_at'] = pd.to_datetime(pull_request_df['merged_at'])
    pull_request_df['merge_time'] = (pull_request_df['merged_at'] - pull_request_df['created_at']).dt.total_seconds() / 3600

    fig = make_subplots(
        rows=3, cols=3,
        subplot_titles=(
            "Total Commits", "Commit Frequency", "Commits Heatmap",
            "Total Pull Requests", "PR Merge Time", "PRs Per Developer",
            "Issues Open vs Closed", "Avg Issue Resolution Time", "Top Contributors to Issue Resolution"
        ),
        specs=[
            [{"type": "indicator"}, {"type": "bar"}, {"type": "heatmap"}],
            [{"type": "indicator"}, {"type": "box"}, {"type": "bar"}],
            [{"type": "pie"}, {"type": "bar"}, {"type": "bar"}]
        ]
    )

    fig.add_trace(go.Indicator(mode="number", value=commits_df.shape[0], title={"text": "Total Commits"}), row=1, col=1)

    top_committers = commits_df['author'].value_counts().head(10)
    fig.add_trace(go.Bar(x=top_committers.index, y=top_committers.values, name='Top 10 Committers'), row=1, col=2)

    heatmap_data = commits_by_day_hour.pivot(index='day_of_week', columns='hour', values='commit_count').fillna(0)
    fig.add_trace(go.Heatmap(z=heatmap_data, x=heatmap_data.columns, y=heatmap_data.index, colorscale='Viridis'), row=1, col=3)

    fig.add_trace(go.Indicator(mode="number", value=pull_request_df.shape[0], title={"text": "Total Pull Requests"}), row=2, col=1)

    fig.add_trace(go.Box(y=pull_request_df['merge_time'], name='PR Merge Time'), row=2, col=2)

    prs_per_developer = pull_request_df['author'].value_counts().head(10)
    fig.add_trace(go.Bar(x=prs_per_developer.index, y=prs_per_developer.values, name='PRs Per Developer'), row=2, col=3)

    issues_state_counts = issues_df['state'].value_counts()
    fig.add_trace(go.Pie(labels=issues_state_counts.index, values=issues_state_counts.values, name='Issues State Distribution'), row=3, col=1)

    avg_resolution_time = issues_df.groupby(issues_df['created_at'].dt.to_period('M'))['resolution_time'].mean().reset_index()
    fig.add_trace(go.Bar(x=avg_resolution_time['created_at'].astype(str), y=avg_resolution_time['resolution_time'], name='Avg Issue Resolution Time'), row=3, col=2)

    top_contributors = issues_df['author'].value_counts().head(10)
    fig.add_trace(go.Bar(x=top_contributors.index, y=top_contributors.values, name='Top Contributors to Issue Resolution'), row=3, col=3)

    fig.update_layout(height=900, width=1200, title_text="Developer Performance Dashboard", showlegend=False)

    return fig
