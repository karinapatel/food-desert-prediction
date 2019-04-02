from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import datetime,timedelta
from pymongo import MongoClient
import yaml
import time
import nltk
from twitter import *
nltk.download('vader_lexicon')

#180 rate limit

#function to pull secret data
def load_api_key(filename='twitter_api_key.yaml'):
    """Load Yelp API client ID and client secret and return them as a dictionary."""
    with open(filename) as f:
        return yaml.load(f)


# Creating the authentication object
t = Twitter(
    auth=OAuth(access_token, access_token_secret,consumer_key, consumer_secret))

def twitter_180(coll_name,query_list, time_back):
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
                #using twitter wrapper, whould be a search as follows:
                Query = t.search.tweets(q=q,result_type='recent',count=100,tweet_mode='extended')
                c+=1
            else:
                Query = t.search.tweets(q=q,result_type='recent',count=100,max_id=max_id,tweet_mode='extended')
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
            if req_count>178:
                print("sleep time")
                time.sleep(60*15)
                req_count = 0
    #finally done!!!
    print("finished pull")

#mongo query for coord data: db.twitter.find({"full_data.geo" : {$exists : true,$ne : null}}).count()

if __name__ == "__main__":
    #start up mongo server and connect to the client
    client = MongoClient()
    db = client['capstone']
    coll=db['twitter']  

    #get secret data to call api
    key = load_api_key()
    consumer_key = key['consumer_key']
    consumer_secret = key['consumer_secret']
    access_token = key['access_token']
    access_token_secret = key['access_token_secret']

    #create sentiment object
    sid = SentimentIntensityAnalyzer()
 
    #healthy foods list
    healthy = pd.read_csv('data/twitter_queries/healthy.csv', header = None)
    healthy_foods = list(healthy[0])

    #unhealthy foods list
    unhealthy = pd.read_csv('data/twitter_queries/unhealthy.csv', header = None)
    unhealthy_foods = list(unhealthy[0])

    grocery = pd.read_csv('data/twitter_queries/grocery_list.csv',header=None)[0]

    fast_foods = pd.read_csv('data/twitter_queries/fast_foods.csv',header=None)[0]

    
    #pull the data
    twitter_180('twitter',['safeway', 'albertsons'], 1)