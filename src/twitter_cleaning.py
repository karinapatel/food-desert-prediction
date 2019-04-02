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

#subset of data in US and formatted correctly
def prep_twitter_df(df):
    #create coords feature
    df['coords'] = df['full_data'].apply(lambda x: x['geo']['coordinates'])
    
    code = []
    for i in df['full_data']:
        if i['place']:
            code.append(i['place']['country_code'])
        else:
            code.append(None)
    code = np.array(code)
    #get only data tweeted from US
    us_df = df[code=="US"]
    
    #split out lat, long, text, and sentiment
    us_df['lat'] = us_df.coords.apply(lambda x: x[0])
    us_df['long'] = us_df.coords.apply(lambda x: x[1])
    
    us_df['text'] = us_df['text'].apply(clean_text)
    
    us_df['sentiment'] = us_df['text'].apply(lambda x: sid.polarity_scores(x))
    
    #return subset df
    return us_df

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

#does everything at above scripts do in a function
def pull_to_csv(coll_name,path_for_csv):
    #get geotagged data
    df1 = pull_geodata(coll_name)
    #tweets from US only
    us_df = prep_twitter_df(df1)
    #add census data to df
    census_update = census_df(us_df)
    #save to csv
    census_update.to_csv(path_for_csv)
    return census_update



if __name__ == "__main__":

    client = MongoClient()
    db = client['capstone']

    sid = SentimentIntensityAnalyzer() 
    
    #replace these with your collection data 
    healthy_df = pull_geodata('healthy')
    us_healthy = prep_twitter_df(healthy_df)
    census_healthy = census_df(us_healthy)
    census_healthy.to_csv("data/census_healthy1.csv")

    #OR

    census_healthy = pull_to_csv('healthy',"data/census_healthy1.csv")
    