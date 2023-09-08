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
    request = None
    main(request)

# import tweepy
# import json

# auth_dict=json.load(open('auth.json'))

# oauth2_user_handler = tweepy.OAuth2UserHandler(
#     client_id=auth_dict['client_id'],
#     redirect_uri="https://simpsonshaiku.com",
#     scope=["tweet.read", "tweet.write"],
#     # Client Secret is only necessary if using a confidential client
#     client_secret=auth_dict["client_secret"],
# )

# # oauth2_user_handler._client.code_verifier = "6sklXi1DTghv4eDyOp4coRIlF5md9a_dUhSvqLabocrqMe5VI93uAE4KwRN6WFxEIE0jLuCVY9YnZt_hP5N4UQ"
# # oauth2_user_handler._client.code_challenge = "yfCkb0Bn7hJAz50OGXE-H50AXeO8pX38nnRU9jDdHgU"

# # print(dir(oauth2_user_handler._client))
# # response_url = oauth2_user_handler.get_authorization_url()
# # print(response_url)

# access_token = oauth2_user_handler.fetch_token(
#     "https://simpsonshaiku.com/?state=AwSqAEAsQJk9PMNkMvz8C11RXyWGAV&code=dFB2d2VjRVJaVktWNjlyTDNJZkl5NjY3Yk1yUGM4TTB0TlFBemxGN3J6bHo1OjE2OTQxMjkwNDE5MTQ6MToxOmFjOjE"
# )

# client = tweepy.Client(access_token['access_token'])
# client.create_tweet('v2 API test')
