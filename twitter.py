import os
import json
import tweepy
import tempfile
import compuglobal
import requests
import numpy as np
from datetime import datetime

from haiku import SimpsonsHaiku

class SimpsonsTwitterBot():


    def __init__(self, auth_dict=None, haiku_df=None):
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


    def tweet_haiku(self, media_reply=True, media_type='jpg', add_metadata=True,
                    caption=False, golden_age=False):
        """Load SimpsonsHaiku object and sample and tweet a haiku."""
        simpsons_haiku = SimpsonsHaiku(self.haiku_df)
        haiku, metadata = simpsons_haiku.generate_haiku(golden_age=golden_age)

        tweet = self.api.update_status(haiku)
        tweet_id = tweet._json['id']
        print('Haiku tweeted')
        
        if media_reply:
            
            episode_key = 'S{:02d}E{:02d}'.format(
                metadata['season'].values[0], metadata['number_in_season'].values[0]
            )

            if add_metadata:
                q = '{} {}'.format(episode_key, metadata['title'].values[0])
            else:
                q = ''

            # First try
            image_url, meme_url, gif_url, mp4_url = self.search_frinkiac(haiku, episode_key)
            # Second try
            if image_url is None and meme_url is None and gif_url is None and mp4_url is None:
                haiku_end = '\n'.join(haiku.split('\n')[1:])
                image_url, meme_url, gif_url, mp4_url = self.search_frinkiac(haiku_end, episode_key)
            # Third try
            if image_url is None and meme_url is None and gif_url is None and mp4_url is None:
                haiku_start = '\n'.join(haiku.split('\n')[:2])
                image_url, meme_url, gif_url, mp4_url = self.search_frinkiac(haiku_start, episode_key)

            if image_url is None and meme_url is None and gif_url is None and mp4_url is None:
                self.api.update_status(q, in_reply_to_status_id=tweet_id)
                return "No Frinkiac result found."

            if media_type == 'jpg':
                if caption:
                    media = requests.get(meme_url).content
                else:
                    media = requests.get(image_url).content
            elif media_type == 'gif':
                media = requests.get(gif_url).content
            elif media_type == 'mp4':
                media = requests.get(mp4_url).content

            tmpdir = tempfile.gettempdir()
            media_filename = '{}/media.{}'.format(tmpdir, media_type)
            with open(media_filename, 'wb') as handler:
                handler.write(media)

            if media_type == 'gif':
                media_id = self.api.chunked_upload(media_filename, media_category='tweet_gif').media_id
            else:
                media_id = self.api.media_upload(media_filename).media_id
                
            self.api.update_status(q, media_ids=[media_id], in_reply_to_status_id=tweet_id)

            print('Media reply tweeted')


    def search_frinkiac(self, query, episode_key):
        """Search Frinkiac using the haiku and return URL to image, gif, and mp4."""

        simpsons = compuglobal.Frinkiac()
        query = query.replace('\n', ' ')

        # Caption formatting
        caption = simpsons.format_caption(query, max_lines=3)

        image_url, meme_url, gif_url, mp4_url = None, None, None, None
        search_results = simpsons.search(query)
        for result in search_results:
            if result.key == episode_key:
                screencap = simpsons.get_screencap(result.key, 
                                                   result.timestamp)
                image_url = screencap.get_image_url()
                meme_url = screencap.get_meme_url(caption)
                gif_url = screencap.get_gif_url()
                mp4_url = screencap.get_mp4_url()
                break
        
        return image_url, meme_url, gif_url, mp4_url


if __name__ == '__main__':

    try:
        # Local version
        auth_dict=json.load(open('auth.json'))
    except:
        # GCP version
        auth_dict = {
            'api_key': os.environ.get("CONSUMER_KEY"),
            'api_key_secret': os.environ.get("CONSUMER_SECRET"),
            'access_token': os.environ.get("ACCESS_TOKEN"),
            'access_token_secret': os.environ.get("ACCESS_TOKEN_SECRET")
        }

    simpsons_bot = SimpsonsTwitterBot(
        auth_dict=auth_dict,
        haiku_df='haiku_df.csv'
    )

    # Select media type at random
    media_type = np.random.choice(['jpg', 'gif'])

    # "Golden-age Wednesdays"
    day = datetime.today().weekday()
    golden_age = True if day == 2 else False

    # Tweet on, son, tweet on!
    simpsons_bot.tweet_haiku(media_reply=True, media_type=media_type, 
                             add_metadata=True, golden_age=golden_age)