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


    def tweet_haiku(self, media_reply=True, media_type='jpg', add_metadata=True):
        """Load SimpsonsHaiku object and sample and tweet a haiku."""
        simpsons_haiku = SimpsonsHaiku(self.haiku_df)
        haiku, metadata = simpsons_haiku.generate_haiku()

        tweet = self.api.update_status(haiku)
        tweet_id = tweet._json['id']
        
        if media_reply:
            
            episode_key = 'S{:02d}E{:02d}'.format(
                metadata['season'].values[0], metadata['number_in_season'].values[0]
            )

            if add_metadata:
                q = '{} {}'.format(episode_key, metadata['title'].values[0])
            else:
                q = ''

            image_url, gif_url, mp4_url = self.search_frinkiac(haiku, episode_key)

            if image_url is None and gif_url is None and mp4_url is None:
                self.api.update_status(q, in_reply_to_status_id=tweet_id)
                return "No Frinkiac result found."

            if media_type == 'jpg':
                media = requests.get(image_url).content
            elif media_type == 'gif':
                media = requests.get(gif_url).content
            elif media_type == 'mp4':
                media = requests.get(mp4_url).content

            media_filename = 'media.{}'.format(media_type)
            with open(media_filename, 'wb') as handler:
                handler.write(media)

            media_id = self.api.media_upload(media_filename).media_id
            self.api.update_status(q, media_ids=[media_id], in_reply_to_status_id=tweet_id)


    def search_frinkiac(self, query, episode_key):
        """Search Frinkiac using the haiku and return URL to image and gif."""

        simpsons = compuglobal.Frinkiac()
        query = query.replace('\n', ' ')

        gif_url, image_url, mp4_url = None, None, None
        search_results = simpsons.search(query)
        for result in search_results:
            if result.key == episode_key:
                screencap = simpsons.get_screencap(result.key, 
                                                   result.timestamp)
                image_url = screencap.get_image_url()
                gif_url = screencap.get_gif_url()
                mp4_url = screencap.get_mp4_url()
                break
        
        return image_url, gif_url, mp4_url


if __name__ == '__main__':

    simpsons_bot = SimpsonsTwitterBot(
        auth_dict=json.load(open('auth.json')), 
        haiku_df='haiku_df.csv'
    )

    print(simpsons_bot.tweet_haiku(media_reply=True, media_type='jpg', add_metadata=True))
    
    # for tweet in simpsons_bot.api.home_timeline():
    #     print(tweet._json['text'])