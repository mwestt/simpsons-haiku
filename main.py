import os
import json
import nltk
import numpy as np
from datetime import datetime

from twitter import SimpsonsTwitterBot


def main(request):
    
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

    nltk.download('cmudict')

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

    return 'Tweet on, son! Tweet on!'


if __name__ == '__main__':
    main()
