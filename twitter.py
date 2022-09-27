import json
import tweepy
import pandas as pd

from haiku import SimpsonsHaiku

class SimpsonsTwitterBot():


    def __init__(self, auth_dict=json.load(open('auth.json')), haiku_df=None):
        self.auth_dict = auth_dict
        self.API_KEY = self.auth_dict['api_key']
        self.API_SECRET = self.auth_dict['api_key_secret']
        self.ACCESS_TOKEN = self.auth_dict['access_token']
        self.ACCESS_SECRET = self.auth_dict['access_token_secret']
        self.api = self.authenticate()
        self.haiku_df = haiku_df


    def authenticate(self):
        """Authenticate using OAuth1."""
        auth = tweepy.OAuth1UserHandler(
            self.API_KEY, self.API_SECRET, self.ACCESS_TOKEN, self.ACCESS_SECRET
        )
        api = tweepy.API(auth)

        return api


    def tweet_haiku(self, media=False):
        """Load SimpsonsHaiku object and sample and tweet a haiku."""
        simpsons_haiku = SimpsonsHaiku(self.haiku_df)
        haiku = simpsons_haiku.generate_haiku()

        if media:
            pass  # TODO add media tweeting functionality, with Frinkiac
        else:
            self.api.update_status(haiku)


if __name__ == '__main__':
    
    simpsons_bot = SimpsonsTwitterBot(
        auth_dict=json.load(open('auth.json')), 
        haiku_df='haiku_df.csv'
    )

    simpsons_bot.tweet_haiku()
    
    for tweet in simpsons_bot.api.home_timeline():
        print(tweet._json['text'])