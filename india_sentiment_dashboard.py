# -----------------------------
# india_sentiment_dashboard_final.py
# -----------------------------

import streamlit as st
import tweepy
import pandas as pd
import matplotlib.pyplot as plt
from textblob import TextBlob
from wordcloud import WordCloud, STOPWORDS

# -----------------------------
# Twitter API Authentication
# -----------------------------
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAIA34gEAAAAAPVDfrGnqYneeFtziMYFg4XC9LF4%3DXPJZd5cFT88eLnXrLbzG8QxLQ2wZ4ThfUAFG0zVeXSlj0NheiQ"
client = tweepy.Client(bearer_token=BEARER_TOKEN, wait_on_rate_limit=True)

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("Twitter Sentiment Dashboard (Fast + WordCloud + Trend)")
keyword = st.text_input("Enter Keyword / Hashtag / Query:", "Pakistan")
max_results = st.slider("Max Tweets to Fetch:", 5, 20, 10)  # Small batch for speed

# -----------------------------
# Fast Fetch Function
# -----------------------------
def fetch_tweets_fast(query, max_results=10):
    all_tweets = []
    try:
        final_query = f"{query}"  # optional: add '-is:retweet lang:en' if needed
        response = client.search_recent_tweets(
            query=final_query,
            tweet_fields=["created_at", "geo", "lang", "public_metrics"],
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
    except Exception as e:
        st.error(f"Error fetching tweets: {e}")
    return all_tweets

# -----------------------------
# Main Logic
# -----------------------------
if st.button("Fetch Tweets"):
    st.info("Fetching tweets...")
    tweets = fetch_tweets_fast(keyword, max_results)
    
    if tweets:
        df = pd.DataFrame(tweets)
        st.success(f"Fetched {len(df)} tweets")
        st.dataframe(df)

        # -----------------------------
        # Language Pie Chart
        # -----------------------------
        st.subheader("Language Distribution")
        lang_counts = df['lang'].value_counts()
        fig1, ax1 = plt.subplots()
        ax1.pie(lang_counts, labels=lang_counts.index, autopct='%1.1f%%', startangle=140)
        ax1.axis('equal')
        st.pyplot(fig1)

        # -----------------------------
        # Sentiment Analysis Pie Chart
        # -----------------------------
        st.subheader("Sentiment Analysis")
        df['sentiment'] = df['text'].apply(lambda x: TextBlob(x).sentiment.polarity)
        df['sentiment_label'] = df['sentiment'].apply(
            lambda x: 'Positive' if x > 0 else ('Negative' if x < 0 else 'Neutral')
        )
        sentiment_counts = df['sentiment_label'].value_counts()
        fig2, ax2 = plt.subplots()
        ax2.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', startangle=140)
        ax2.axis('equal')
        st.pyplot(fig2)

        # -----------------------------
        # WordCloud (ignoring stopwords and hashtags)
        # -----------------------------
        st.subheader("WordCloud of Tweets")
        all_text = " ".join(df['text'].tolist())
        stopwords = set(STOPWORDS)
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color='white',
            stopwords=stopwords,
            collocations=False
        ).generate(all_text)
        fig_wc, ax_wc = plt.subplots(figsize=(10, 5))
        ax_wc.imshow(wordcloud, interpolation='bilinear')
        ax_wc.axis('off')
        st.pyplot(fig_wc)

        # -----------------------------
        # Date-wise Tweet Trend
        # -----------------------------
        st.subheader("Tweet Trend Over Time")
        df['date'] = pd.to_datetime(df['created_at']).dt.date
        trend = df.groupby('date').size()
        fig_trend, ax_trend = plt.subplots()
        trend.plot(kind='line', marker='o', ax=ax_trend)
        ax_trend.set_xlabel("Date")
        ax_trend.set_ylabel("Number of Tweets")
        ax_trend.set_title("Tweet Trend Over Time")
        plt.tight_layout()
        st.pyplot(fig_trend)

        # -----------------------------
        # Top 5 Liked Tweets
        # -----------------------------
        st.subheader("Top 5 Liked Tweets")
        top_likes = df.nlargest(5, 'likes')
        fig3, ax3 = plt.subplots()
        ax3.barh(top_likes['text'], top_likes['likes'], color='skyblue')
        ax3.set_xlabel("Likes")
        ax3.set_ylabel("Tweet")
        ax3.set_title("Top 5 Liked Tweets")
        plt.tight_layout()
        st.pyplot(fig3)

        # -----------------------------
        # Top 5 Retweeted Tweets
        # -----------------------------
        st.subheader("Top 5 Retweeted Tweets")
        top_retweets = df.nlargest(5, 'retweets')
        fig4, ax4 = plt.subplots()
        ax4.barh(top_retweets['text'], top_retweets['retweets'], color='orange')
        ax4.set_xlabel("Retweets")
        ax4.set_ylabel("Tweet")
        ax4.set_title("Top 5 Retweeted Tweets")
        plt.tight_layout()
        st.pyplot(fig4)

    else:
        st.warning("No tweets found. Try a different keyword or increase max results.")
