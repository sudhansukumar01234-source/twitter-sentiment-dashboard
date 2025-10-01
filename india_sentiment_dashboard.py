# -----------------------------
# streamlit_twitter_dashboard.py (Optimized Version)
# -----------------------------

import streamlit as st
import tweepy
import pandas as pd
import matplotlib.pyplot as plt
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# -----------------------------
# Twitter API Authentication
# -----------------------------
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAADs64gEAAAAARicDLnHNcwLF%2BAVtZFkWs4qBurs%3D0pnuLJ3ZuGO2dsd7YKX6fMv41UzjuPKaTkf1Uf8VvFN5SiaSF9"  # replace with your token
client = tweepy.Client(bearer_token=BEARER_TOKEN, wait_on_rate_limit=True)

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("Twitter Sentiment Dashboard")
keyword = st.text_input("Enter Keyword / Hashtag / Query:", "Pakistan")
max_results = st.slider("Max Tweets to Fetch:", 10, 100, 30)

# -----------------------------
# Function to fetch tweets (cached)
# -----------------------------
@st.cache_data(ttl=300)  # cache for 5 minutes
def fetch_tweets(query, max_results=50):
    all_tweets = []
    try:
        final_query = f"{query} -is:retweet lang:en"
        response = client.search_recent_tweets(
            query=final_query,
            tweet_fields=["created_at", "lang", "public_metrics"],
            max_results=max_results
        )
        if response.data:
            for tweet in response.data:
                all_tweets.append({
                    "text": tweet.text,
                    "created_at": tweet.created_at,
                    "lang": tweet.lang,
                    "retweets": tweet.public_metrics.get("retweet_count"),
                    "likes": tweet.public_metrics.get("like_count")
                })
    except tweepy.TooManyRequests:
        st.error("⚠️ Rate limit reached. Try again later.")
        return []
    return all_tweets

# -----------------------------
# Main Logic
# -----------------------------
if st.button("Fetch Tweets"):
    st.info("Fetching tweets...")
    tweets = fetch_tweets(keyword, max_results)

    if tweets:
        df = pd.DataFrame(tweets)
        st.success(f"Fetched {len(df)} tweets")
        st.dataframe(df)

        # -----------------------------
        # Sentiment Analysis (VADER)
        # -----------------------------
        sia = SentimentIntensityAnalyzer()
        df['sentiment'] = df['text'].apply(lambda x: sia.polarity_scores(x)['compound'])
        df['sentiment_label'] = df['sentiment'].apply(
            lambda x: 'Positive' if x > 0 else ('Negative' if x < 0 else 'Neutral')
        )

        # -----------------------------
        # Sentiment Pie Chart
        # -----------------------------
        st.subheader("Sentiment Analysis (Pie Chart)")
        sentiment_counts = df['sentiment_label'].value_counts()
        colors = ['green' if label == 'Positive' else 'red' if label == 'Negative' else 'gray'
                  for label in sentiment_counts.index]
        fig1, ax1 = plt.subplots()
        ax1.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%',
                startangle=140, colors=colors)
        ax1.axis('equal')
        st.pyplot(fig1)

        # -----------------------------
        # Sentiment Bar Chart
        # -----------------------------
        st.subheader("Sentiment Analysis (Bar Chart)")
        fig2, ax2 = plt.subplots()
        sentiment_counts.plot(kind='bar', ax=ax2, color=colors)
        ax2.set_xlabel("Sentiment")
        ax2.set_ylabel("Number of Tweets")
        ax2.set_title("Sentiment Distribution")
        st.pyplot(fig2)

        # -----------------------------
        # Top 5 Liked Tweets
        # -----------------------------
        st.subheader("Top 5 Liked Tweets")
        top_likes = df.nlargest(5, 'likes')
        top_likes['short_text'] = top_likes['text'].apply(lambda x: x[:50] + "..." if len(x) > 50 else x)
        fig3, ax3 = plt.subplots()
        ax3.barh(top_likes['short_text'], top_likes['likes'], color='skyblue')
        ax3.set_xlabel("Likes")
        ax3.set_title("Top 5 Liked Tweets")
        plt.tight_layout()
        st.pyplot(fig3)

        # -----------------------------
        # Top 5 Retweeted Tweets
        # -----------------------------
        st.subheader("Top 5 Retweeted Tweets")
        top_retweets = df.nlargest(5, 'retweets')
        top_retweets['short_text'] = top_retweets['text'].apply(lambda x: x[:50] + "..." if len(x) > 50 else x)
        fig4, ax4 = plt.subplots()
        ax4.barh(top_retweets['short_text'], top_retweets['retweets'], color='orange')
        ax4.set_xlabel("Retweets")
        ax4.set_title("Top 5 Retweeted Tweets")
        plt.tight_layout()
        st.pyplot(fig4)

    else:
        st.warning("No tweets found. Try a different keyword or later.")
