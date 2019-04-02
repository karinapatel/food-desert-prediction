from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import datetime,timedelta
from pymongo import MongoClient
import yaml
import time
import nltk
from twitter import *
nltk.download('vader_lexicon')

#180 rate limit
#start up mongo server and connect to the client
client = MongoClient()
db = client['capstone']
coll=db['twitter']  

#function to pull secret data
def load_api_key(filename='twitter_api_key.yaml'):
    """Load Yelp API client ID and client secret and return them as a dictionary."""
    with open(filename) as f:
        return yaml.load(f)

#get secret data to call api
key = load_api_key()
consumer_key = key['consumer_key']
consumer_secret = key['consumer_secret']
access_token = key['access_token']
access_token_secret = key['access_token_secret']

# Creating the authentication object
t = Twitter(
    auth=OAuth(access_token, access_token_secret,consumer_key, consumer_secret))

#creating sentiment object from SentimentIntensityAnalyzer module
sid=SentimentIntensityAnalyzer()

#actual script to query and store in mongo, keep track of req_count so you don't exceed rate limit...sleep before you do it

#words = ['safeway','albertsons','ralphs','kroger','trader joe\'s','whole foods','jewel-osco', 'pavilions', 'food 4 less']
words=['randalls','tom thumb','star market','vons','united supermarkets','amigos','acme markets', 'carrs']
#keep count of requests made so I don't keep hitting rate limit
req_count = 0
#iterate through words of interest
for query in words:
    
    #find current time and keep track of how far back to query
    current = datetime.now()
    Prior = datetime.now() - timedelta(days=1)
    
    #initialize lists
    #check if it is initial query
    c = 0
    #tweet text for current query
    lst = []
    #tweet ids
    s = []
    # filter out RT to avoid duplicates
    q = query + " -filter:retweets"
    while current>Prior:
        if c == 0:
            Query = t.search.tweets(q=q,result_type='recent',count=100,tweet_mode='extended')
            next_cursor = Query['search_metadata']['next_results']
            c+=1
        else:
            Query = t.search.tweets(q=q,result_type='recent',count=100,max_id=max_id,tweet_mode='extended')
            next_cursor = Query['search_metadata']['next_results']
            c+=1
        for i,tweet in enumerate(Query['statuses']):
            if tweet['id'] not in s and query in tweet['full_text'].lower():
                date = tweet['created_at']
                current = datetime.strptime(date, '%a %b %d %H:%M:%S +0000 %Y')
                lst.append(tweet['full_text'])
                s.append(tweet['id'])
                ss = sid.polarity_scores(tweet['full_text'])
                coll.insert_one({'full_data': tweet,'text': tweet['full_text'], 'sentiment':ss})
            req_count+=1
        max_id = tweet['id']
        if req_count>450*99:
            time.sleep(60*15)
            req_count = 0


#mongo query for coord data: db.twitter.find({"full_data.geo" : {$exists : true,$ne : null}}).count()