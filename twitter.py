import json
from stringprep import in_table_a1
import tweepy
import compuglobal
import requests
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


    def tweet_haiku(self, media_reply=False, media_type='gif'):
        """Load SimpsonsHaiku object and sample and tweet a haiku."""
        simpsons_haiku = SimpsonsHaiku(self.haiku_df)
        haiku, metadata = simpsons_haiku.generate_haiku()

        tweet = self.api.update_status(haiku)
        tweet_id = tweet._json['id']
        
        if media_reply:
            image_url, gif_url = self.search_frinkiac(haiku)

            if media_type == 'jpg':
                media = requests.get(image_url).content
            elif media_type == 'gif':
                media = requests.get(gif_url).content

            media_filename = 'media.{}'.format(media_type)
            with open(media_filename, 'wb') as handler:
                handler.write(media)

            media_id = self.api.media_upload(media_filename).media_id
            self.api.update_status('', media_ids=[media_id], in_reply_to_status_id=tweet_id)


    def search_frinkiac(self, query):
        """Search Frinkiac using the haiku and return URL to image and gif."""
        simpsons = compuglobal.Frinkiac()
        screencap = simpsons.search_for_screencap(query)  # TODO Expand this search and use episode metadata
        image_url = screencap.get_meme_url()
        gif_url = screencap.get_gif_url()
        
        return image_url, gif_url


if __name__ == '__main__':

    simpsons_bot = SimpsonsTwitterBot(
        auth_dict=json.load(open('auth.json')), 
        haiku_df='haiku_df.csv'
    )

    simpsons_bot.tweet_haiku(media_reply=True)
    
    for tweet in simpsons_bot.api.home_timeline():
        print(tweet._json['text'])