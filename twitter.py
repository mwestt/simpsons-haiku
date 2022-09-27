import json
import tweepy

from haiku import SimpsonsHaiku

class SimpsonsTwitterBot():

    def __init__(self, auth_dict=json.load(open('auth.json'))):
        self.auth_dict = auth_dict
        self.API_KEY = self.auth_dict['api_key']
        self.API_SECRET = self.auth_dict['api_key_secret']
        self.ACCESS_TOKEN = self.auth_dict['access_token']
        self.ACCESS_SECRET = self.auth_dict['access_token_secret']


    def authenticate(self):

        auth = tweepy.OAuth1UserHandler(
            self.API_KEY, self.API_SECRET, self.ACCESS_TOKEN, self.ACCESS_SECRET
        )

        api = tweepy.API(auth)
        self.api = api

        return api


# tweet = 'Second test!'
# api.update_status(tweet)

if __name__ == '__main__':
    simpsons_bot = SimpsonsTwitterBot()
    for tweet in simpsons_bot.authenticate().home_timeline():
        print(tweet._json['text'])