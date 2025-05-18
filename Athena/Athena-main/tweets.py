import requests
import streamlit as st
import streamlit.components.v1 as components
import sys

# Make sure to put your Twitter Bearer token in Streamlit secrets under 'bearer_token'
bearer_token = st.secrets["bearer_token"]

def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

def connect_to_endpoint(url, params):
    response = requests.get(url, auth=bearer_oauth, params=params)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

def get_tweet_embed_html(tweet_url):
    api_url = f'https://publish.twitter.com/oembed?url={tweet_url}&theme=dark'
    response = requests.get(api_url)
    return response.json().get("html", "")

def show_tweets(search_query):
    search_url = "https://api.twitter.com/2/tweets/search/recent"
    params = {'query': search_query, 'tweet.fields': 'author_id', 'max_results': 10}
    
    try:
        json_response = connect_to_endpoint(search_url, params)
        for tweet in json_response.get("data", []):
            author_id = tweet.get("author_id")
            tweet_id = tweet.get("id")
            url = f'https://twitter.com/{author_id}/status/{tweet_id}'
            embed_html = get_tweet_embed_html(url)
            components.html(embed_html, height=300)
    except Exception as e:
        st.error(f"Error fetching tweets: {e}")
        st.info("Try searching for different hashtags or keywords.")
