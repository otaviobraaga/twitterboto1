import tweepy
import keys
from time import sleep
import datetime
import os
import re

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


def retweet(tweepy_api: tweepy.API, hashtag: str, delay=60, items=100):
    print(f"*** \n{datetime.datetime.now()}\n***")

    tweet_ids = read_tweet_ids()

    for tweet in tweepy.Cursor(tweepy_api.search_tweets, q=f"{hashtag} @hey_wallet send \"to the first\"").items(items):
        try:
            tweet_id = dict(tweet._json)["id"]
            tweet_text = clean_text(dict(tweet._json)["text"])

            if str(tweet_id) in tweet_ids:
                print(f"Skipping retweet of tweet {tweet_id}")
                continue

            print("id: " + str(tweet_id))
            print("text: " + str(tweet_text)[0:70] + "..." )

            tweepy_api.retweet(tweet_id)
            tweepy_api.create_favorite(tweet_id)
            save_tweet_id(tweet_id)

        except tweepy.TweepyException as error:
            print(error)
            sleep(.5)

    print("")
    sleep(delay)

if __name__ == '__main__':
    api = api()

    while True:
        retweet(api, ["Quai", "Quai Network" , "@QuaiNetwork"], delay=30, items=200)
