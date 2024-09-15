import streamlit as st
import os
import pandas as pd
from data_collection.github_api import GitHubDataCollector
from metrics.calculator import calculate_metrics
from visualization.charts import generate_charts
from query_interface.nlp_processor import process_query
import plotly.express as px

st.set_page_config(page_title="GitHub Developer Performance Dashboard", layout="wide")

st.title('GitHub Developer Performance Dashboard')

repo_url = st.text_input('Enter GitHub Repository URL:')
access_token = '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'  

commit_csv_path = 'commits.csv'
pr_csv_path = 'pull_requests.csv'
issue_csv_path = 'issues.csv'
review_csv_path = 'code_reviews.csv'
metrics_csv_path = 'calculated_metrics.csv'

def load_saved_metrics():
    try:
        return pd.read_csv(metrics_csv_path)
    except FileNotFoundError:
        return None

def save_metrics_to_csv(metrics):
    pd.DataFrame(metrics).to_csv(metrics_csv_path, index=False)

def load_data():
    data = {}
    data['commits'] = pd.read_csv(commit_csv_path)
    data['pull_requests'] = pd.read_csv(pr_csv_path)
    data['issues'] = pd.read_csv(issue_csv_path)
    data['reviews'] = pd.read_csv(review_csv_path)
    return data
    

if st.button('Fetch Data'):
    if not repo_url or not access_token:
        st.error('Please enter both GitHub Repository URL and Access Token.')
    else:
        with st.spinner('Fetching new data...'):
            os.environ['GITHUB_ACCESS_TOKEN'] = access_token
            collector = GitHubDataCollector()
            collector.save_data_to_csv(repo_url, commit_csv_path, pr_csv_path, issue_csv_path, review_csv_path)
     
            data = load_data()
            if data:
                metrics = calculate_metrics(
                    data['commits'],
                    data['pull_requests'],
                    data['issues']
                )
                save_metrics_to_csv(metrics)
                st.success("New data fetched and metrics updated successfully!")
            else:
                st.error("Error loading data after fetching.")

data = load_data()

if data:
    try:
        data['commits']['author'] = data['commits']['author'].astype(str)
        data['pull_requests']['author'] = data['pull_requests']['author'].astype(str)
        data['issues']['author'] = data['issues']['author'].astype(str)
        data['reviews']['reviewer'] = data['reviews']['reviewer'].astype(str)

        all_users = pd.concat([ 
            data['commits']['author'],
            data['pull_requests']['author'],
            data['issues']['author'],
            data['reviews']['reviewer']
        ]).unique()

        selected_user = st.sidebar.selectbox('Filter by User', ['All Users'] + list(all_users))

        if selected_user != 'All Users':
            data['commits'] = data['commits'][data['commits']['author'] == selected_user]
            data['pull_requests'] = data['pull_requests'][data['pull_requests']['author'] == selected_user]
            data['issues'] = data['issues'][data['issues']['author'] == selected_user]
            data['reviews'] = data['reviews'][data['reviews']['reviewer'] == selected_user]

        st.subheader(f"Developer Performance Dashboard - {selected_user}")
        dashboard_fig = generate_charts(
            data['commits'],
            data['issues'],
            data['pull_requests']
        )
        st.plotly_chart(dashboard_fig)

        metrics_df = load_saved_metrics()
        if metrics_df is not None:
            st.write("### Developer Metrics")

            col1, col2 = st.columns(2)

            with col1:
                st.write("#### Commit Frequency Bar Chart")
                fig_bar = px.bar(
                    metrics_df, 
                    x="commit_frequency", 
                    y="author", 
                    title="Commit Frequency by Developer"
                )
                st.plotly_chart(fig_bar, use_container_width=True)

            with col2:
                st.write("#### PR Merge Rate Pie Chart")
                fig_pie = px.pie(
                    metrics_df, 
                    values="pr_merge_rate", 
                    names="author", 
                    title="PR Merge Rate by Developer"
                )
                st.plotly_chart(fig_pie, use_container_width=True)

        user_query = st.sidebar.text_input("Ask a question about the data:")
        if user_query:
            try:
                response = process_query(user_query, data['commits'], data['pull_requests'], data['issues'], data['reviews'], selected_user)
                st.sidebar.write("### Chatbot Conversation:")
                st.sidebar.write(f"**You**: {user_query}")
                st.sidebar.write(f"**Bot**:")
                for line in response:
                    st.sidebar.write(line)
            except Exception as e:
                st.error(f"Error processing query: {e}")
    except Exception as e:
        st.error(f"Error generating visualizations: {e}")
