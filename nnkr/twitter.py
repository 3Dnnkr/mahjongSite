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

def get_embeds():
    api = get_api()
    statuses = api.user_timeline()
    embeds = []

    for status in statuses:
        tweet_id = status.id
        screen_id = status.user.screen_name
        url = "https://twitter.com/{}/status/{}".format(screen_id,tweet_id)
        embeds.append(api.get_oembed(url=url,omit_script=True)['html'])

    return embeds