import tweepy
import yaml

def load_api_key(filename='twitter_api_key.yaml'):
    """Load Yelp API client ID and client secret and return them as a dictionary."""
    with open(filename) as f:
        return yaml.load(f)
        
#never push up your API keys!!! 
key = load_api_key()
consumer_key = key['consumer_key']
consumer_secret = key['consumer_secret']
access_token = key['access_token']
access_token_secret = key['access_token_secret']

# Creating the authentication object
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
# Setting your access token and secret
auth.set_access_token(access_token, access_token_secret)
# Creating the API object while passing in auth information
api = tweepy.API(auth) 

# Using the API object to get tweets from your timeline, and storing it in a variable called public_tweets
public_tweets = api.home_timeline()
# foreach through all tweets pulled
for tweet in public_tweets:
   # printing the text stored inside the tweet object
   print("Content: ",tweet.text)
   print()
   print("Location: ",tweet.user.location)

