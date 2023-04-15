import tweepy
import keys
from time import sleep
import datetime
import os
import re
import random

os.environ["PYTHONIOENCODING"] = "utf-8"

def clean_text(text):
    text = re.sub(r'[^\x00-\x7f]',r'', text)
    return text

def api():
    auth = tweepy.OAuthHandler(keys.api_key, keys.api_secret)
    auth.set_access_token(keys.access_token, keys.access_token_secret)

    return tweepy.API(auth)

def read_tweet_ids():
    try:
        with open('tweet_ids.txt', 'r') as f:
            tweet_ids = [line.strip() for line in f]
    except:
        tweet_ids = []
    return tweet_ids

def save_tweet_id(tweet_id):
    file_path = "tweet_ids.txt"
    if os.path.isfile(file_path):
        with open(file_path, "r") as f:
            tweet_ids = [line.strip() for line in f]
            if str(tweet_id) in tweet_ids:
                return  # tweet ID already exists in the file

    with open(file_path, "a") as f:
        f.write(str(tweet_id) + "\n")

def make_post(tweepy_api: tweepy.API):
    post_text = "Hey Folks! Check out the latest news and updates on #cryptocurrency and #airdrops. Follow me and I'll follow back! #follow4follow"
    try:
        tweepy_api.update_status(post_text)
        print("Posted: " + post_text)
    except tweepy.TweepyException as error:
        print(error)
        sleep(.5)

def retweet_comment(tweepy_api: tweepy.API, hashtag: str, delay=60, items=100):
    print(f"*** \n{datetime.datetime.now()}\n***")

    tweet_ids = read_tweet_ids()

    for tweet in tweepy.Cursor(tweepy_api.search_tweets, q=f"{hashtag} -filter:retweets").items(items):
        try:
            tweet_id = dict(tweet._json)["id"]
            tweet_text = clean_text(dict(tweet._json)["text"])

            if str(tweet_id) in tweet_ids:
                print(f"Skipping retweet of tweet {tweet_id}")
                continue

            print("id: " + str(tweet_id))
            print("text: " + str(tweet_text)[0:70] + "..." )

            # Retweet
            tweepy_api.retweet(tweet_id)

            # Like
            tweepy_api.create_favorite(tweet_id)

            # Follow
            username = dict(tweet._json)["user"]["screen_name"]
            tweepy_api.create_friendship(screen_name=username)

            # Save tweet ID
            save_tweet_id(tweet_id)

        except tweepy.TweepyException as error:
            print(error)
            sleep(.5)

    print("")
    sleep(delay)

if __name__ == '__main__':
    api = api()

    while True:
        retweet_comment(api, "#crypto OR #airdrops", delay=30, items=200)
        make_post(api)
        sleep(60 * 60 * 24)  # Wait a day before making another post
