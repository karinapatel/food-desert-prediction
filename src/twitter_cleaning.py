from pymongo import MongoClient
import pandas as pd
import numpy as np
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import requests
import re
import unicodedata
from unidecode import unidecode
import ast
import time

#get data from mongo where there is geocoord info for tweet
def pull_geodata(coll_name):
    coll=db[coll_name]
    query = coll.find({"full_data.geo" : {"$exists" : True,"$ne" : None}})
    df = pd.DataFrame(list(query))
    return df

#remove emojis and urls
def clean_text(inputString):
    final = ""
    for letter in inputString:
        try:
         letter.encode("ascii")
         final += letter
        except UnicodeEncodeError:
         final += ''
    return re.sub(r"http\S+", "", final)

#join census data
#call fcc API to get census associated with lat and long
def get_census(coords):
    url='https://geo.fcc.gov/api/census/area?lat={}&lon={}&format=json'.format(coords[0],coords[1])
    res = requests.get(url)
    if res.json()['results']==[]:
        return None
    else:
        return res.json()['results'][0]['block_fips'][:-4]

#adds the census information to the us df
def census_df(df):
    census = []
    count=0
    req_count=0
    while len(census)< df.shape[0]:
        census.append(get_census(df['coords'].iloc[count]))
        req_count+=1
        count+=1
        if req_count % 1000 == 0:
            print("Current count: ",req_count)
            time.sleep(30)

    df['census']=census
    return df


#subset of data in US and formatted correctly
#pull data from mongo
def pull_geodata(coll_name):
    coll=db[coll_name]
    query = coll.find({"full_data.geo" : {"$exists" : True,"$ne" : None}})
    df = pd.DataFrame(list(query))
    return df

#remove emojis and urls
def clean_text(inputString):
    final = ""
    for letter in inputString:
        try:
         letter.encode("ascii")
         final += letter
        except UnicodeEncodeError:
         final += ''
    return re.sub(r"http\S+", "", final)


def prep_twitter_df(df,category):
    #load target to merge food desert feature
    target = pd.read_csv('data/target.csv')
    #get 11 digit code correct
    target['CensusTract'] = target['CensusTract'].apply(lambda x: "0"+str(x) if len(str(x))==10 else str(x)) 
    
    #get coods data
    df['coords'] = df['full_data'].apply(lambda x: x['geo']['coordinates'])
    
    #only look at US tweets and pull out lat, long, sent
    code = []
    for i in df['full_data']:
        if i['place']:
            code.append(i['place']['country_code'])
        else:
            code.append(None)
    code = np.array(code)
    us_df = df[code=="US"]

    us_df['lat'] = us_df.coords.apply(lambda x: x[0])
    us_df['long'] = us_df.coords.apply(lambda x: x[1])
    
    #remove emojis and urls
    us_df['text'] = us_df['text'].apply(lambda x: re.sub(r"http\S+", "", x))
    
    #calc sentiment on clean text
    us_df['sentiment'] = us_df['text'].apply(lambda x: sid.polarity_scores(x))
    
    #if the sentiment feature is still in str format, convert to dict using ast
    if type(us_df['sentiment'][0]) == str:
        us_df['sentiment'] = us_df['sentiment'].apply(ast.literal_eval)

    #make sure I only get US tweets using hardcode lat long ranges
    us_df = us_df[(us_df['long']>-161)&(us_df['long']<-68)&(us_df['lat']>20)&(us_df['lat']<64)]
    
    #call census api to get the corresponding census data for lat, long data
    us_df = census_df(us_df)

    #get tract in correct 11 digit format
    us_df['census'] = us_df['census'].apply(lambda x: "0"+str(x) if len(str(x))==10 else str(x)) 
    us_df.census=us_df.census.apply(float)
    us_df.dropna(axis=0, inplace=True)
    us_df.census= us_df.census.apply(int)
    us_df['census']=us_df['census'].apply(lambda x: "0"+str(x) if len(str(x))==10 else str(x)) 

    #pull out compound score from sid object
    us_df['comp']=us_df['sentiment'].apply(lambda x: x['compound'])

    #mark the df with the group it came from
    us_df['category']=category

    #merge data with target
    us_df = pd.merge(us_df,target,how='inner',left_on="census",right_on="CensusTract")

    #get county from census
    us_df['county'] = us_df['census'].apply(lambda x: x[:5])
    
    #subset of data useful for analysis
    us_df = us_df[['keyword','text','lat','long','census','comp','category','LILATracts_1And10','county']]
    
    return us_df 

#does everything at above scripts do in a function
def pull_to_csv(coll_name,path_for_csv,category):
    #get geotagged data
    df1 = pull_geodata(coll_name)
    #tweets from US only, sentiment, census
    us_df = prep_twitter_df(df1,category)
    
    return us_df

#takes in collection and path to pull the cleaned data from and insert to mongo
def clean_to_mongo(coll_name, path_to_csv):
    coll=db[coll_name]
    
    df = pd.read_csv(path_to_csv, index_col=0)
    data = df.to_dict(orient='records')
    coll.insert_many(data)
    
#saves the csv data from mongo as a df 
def mongo_to_csv(coll_name,csv_path):
    coll=db[coll_name]
    query = coll.find()
    df = pd.DataFrame(list(query))
    df.to_csv(csv_path)



if __name__ == "__main__":

    client = MongoClient()
    db = client['capstone']
    sid = SentimentIntensityAnalyzer() 
    
    healthy = pull_to_csv('test_db',"data/twitter_mongo/test_data.csv","test")
    unhealthy = pull_to_csv('unhealthy_clean',"data/twitter_mongo/unhealthy_final.csv","unhealthy")
    grocery = pull_to_csv('grocery_stores_clean',"data/twitter_mongo/grocery_stores_final.csv")
    fast_food = pull_to_csv('ff_stores_clean',"data/twitter_mongo/ff_stores_final.csv")

    coll=db['test_db_clean']
    clean_to_mongo('test_db_clean',"data/twitter_mongo/test_data.csv")
    coll.count()

    #combined csv with all data from mongo
    mongo_to_csv('test_db_clean',"data/twitter_mongo/test_clean.csv")
    