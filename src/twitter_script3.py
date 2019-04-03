import yaml
import requests
import base64
import json
from pymongo import MongoClient
import time
from datetime import datetime,timedelta
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd
import re
import unicodedata
from unidecode import unidecode

#450 rate limit
#grabs API keys from secret yaml file so I don't put my keys on github
def load_api_key(filename='twitter_api_key.yaml'):
    """Load Yelp API client ID and client secret and return them as a dictionary."""
    with open(filename) as f:
        return yaml.load(f)

#clean emojis and remove url
def clean_text(inputString):
    final = ""
    for letter in inputString:
        try:
         letter.encode("ascii")
         final += letter
        except UnicodeEncodeError:
         final += ''
    return re.sub(r"http\S+", "", final)

#pulls twitter data and stores in mongo
def twitter_pull(coll_name,query_list, time_back):
    #where to store json data
    coll=db[coll_name]
   
    #keep track of how many requests I make to avoid hitting rate limit 
    req_count = 0

    #iterate through each word I want to pull data for
    for query in query_list:
        print("starting: ",query)

        #account for how much time I want to pull for and initialize lists
        current = datetime.now()
        Prior = datetime.now() - timedelta(days=time_back)
        #keep track of first query
        c = 0 
        #lst to store tweet text
        lst = []
        #lst to store tweet id
        s = []
        #filter out retweets from my search to avoid duplicates
        q = query + " -filter:retweets"
        #until I have reached the amount of time back to pull
        while current>Prior:
            #in this case, no max id since it is the first tweet
            #query according to search params and convert the query as a json
            if c == 0:
                search_params = {
                    'q': q,
                    'lang':'en',
                    'count': 100,
                    'tweet_mode':'extended'
                    #,'geocode':"41.878485,-87.627893,100mi"
                }

                search_url = '{}1.1/search/tweets.json'.format(base_url)

                search_resp = requests.get(search_url, headers=search_headers, params=search_params)
                
                Query = json.loads( search_resp.content )
                
                c+=1
            else:
                #in this case, I am not on my first query so I can use max:id to start from a certain twitter id
                #this is to avoid duplicates in my while loop
                search_params = {
                    'q': q,
                    'lang':'en',
                    'count': 100,
                    'tweet_mode':'extended',
                    'max_id': max_id
                    #,'geocode':"41.878485,-87.627893,100mi",
                }

                search_url = '{}1.1/search/tweets.json'.format(base_url)

                search_resp = requests.get(search_url, headers=search_headers, params=search_params)
                
                Query = json.loads( search_resp.content )
                            
                c+=1

            #once I have my Query, I want to store the data into mongo collection  
            for i,tweet in enumerate(Query['statuses']):
                if tweet['id'] not in s and query in tweet['full_text'].lower():
                    #save date created
                    date = tweet['created_at']
                    
                    #reset my current time so I can continue to propagate back to my timedelta
                    current = datetime.strptime(date, '%a %b %d %H:%M:%S +0000 %Y')
                    
                    #lst of tweet texts
                    tweet_clean = clean_text(tweet['full_text'])
                    
                    lst.append(tweet_clean)
                    
                    #list of tweet ids
                    s.append(tweet['id'])
                    
                    #calculate polarity of tweet
                    ss = sid.polarity_scores(tweet_clean)
                    #here should check if the tweet[id] has already been inserted into mongo to avoid duplicates
                    #also should clean data before calculating sentiment and inserting, can do this later though
                    
                    #insert data into mongo collection
                    coll.insert_one({'full_data': tweet,'text': tweet_clean,'keyword':query, 'sentiment':ss})
            #update request count
            req_count+=1
            #just to keep track of where I am in the loop
            #usually takes hours to complete the query so I want to make sure I am making progress
            
            if req_count % 50 == 0:
                print("current request count: ", req_count)
            #set the max id to be the last id in the query
            max_id = tweet['id']
            
            #sleep for 15 mins if I am approaching the rate limit
            if req_count>448:
                print("sleep time")
                time.sleep(60*15)
                req_count = 0
    #finally done!!!
    print("finished pull")


if __name__ == "__main__":
    #create sentiment object
    sid = SentimentIntensityAnalyzer()
        
    #load in secret keys
    key = load_api_key()

    #grab keys, format them, and encode them (base64)
    client_key = key['consumer_key']
    client_secret = key['consumer_secret']

    key_secret = '{}:{}'.format(client_key, client_secret).encode('ascii')
    b64_encoded_key = base64.b64encode(key_secret)
    b64_encoded_key = b64_encoded_key.decode('ascii')

    #url to get oauth2 aka app auth to get 450 rate limit
    base_url = 'https://api.twitter.com/'
    auth_url = '{}oauth2/token'.format(base_url)

    auth_headers = {
        'Authorization': 'Basic {}'.format(b64_encoded_key),
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
    }

    auth_data = {
        'grant_type': 'client_credentials'
    }

    #post request to get bearer access token
    auth_resp = requests.post(auth_url, headers=auth_headers, data=auth_data)

    access_token = auth_resp.json()['access_token']
    search_headers = {
        'Authorization': 'Bearer {}'.format(access_token)    
    }

    #healthy foods list
    healthy = pd.read_csv('data/twitter_queries/healthy.csv', header = None)
    healthy_foods = list(healthy[0])

    #unhealthy foods list
    unhealthy = pd.read_csv('data/twitter_queries/unhealthy.csv', header = None)
    unhealthy_foods = list(unhealthy[0])

    #grocery_list
    grocery = pd.read_csv('data/twitter_queries/grocery_list.csv',header=None)[0]

    #fast_foods_list
    fast_foods = pd.read_csv('data/twitter_queries/fast_foods.csv',header=None)[0]


    client = MongoClient()
    db = client['capstone']
    #pull the data
    #twitter_pull('test',['safeway', 'albertsons'], 1)

    #time.sleep(15*60)

    #pull more data
    #twitter_pull('healthy',healthy_foods[35:], 2)

    #twitter_pull('unhealthy',unhealthy_foods[20:30], 2)
    #twitter_pull('grocery_stores',words, 44)

    twitter_pull('test_db',['safeway','albertsons'], 1)
