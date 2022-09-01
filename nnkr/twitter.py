import tweepy
import os

def get_api():
    CONSUMER_KEY = os.environ.get('SOCIAL_AUTH_TWITTER_KEY')
    CONSUMER_SECRET = os.environ.get('SOCIAL_AUTH_TWITTER_SECRET')
    ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN')
    ACCESS_SECRET = os.environ.get('TWITTER_ACCESS_SECRET')

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth)
    return api
