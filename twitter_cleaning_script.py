from pymongo import MongoClient
import pandas as pd
import numpy as np
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import requests
import re
import unicodedata
from unidecode import unidecode
import warnings
warnings.filterwarnings('ignore')
import time

def pull_geodata(coll_name):
    coll=db[coll_name]
    query = coll.find({"full_data.geo" : {"$exists" : True,"$ne" : None}})
    df = pd.DataFrame(list(query))
    return df

def clean_text(inputString):
    final = ""
    for letter in inputString:
        try:
         letter.encode("ascii")
         final += letter
        except UnicodeEncodeError:
         final += ''
    return re.sub(r"http\S+", "", final)

def prep_twitter_df(df):
    df['coords'] = df['full_data'].apply(lambda x: x['geo']['coordinates'])
    
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
    
    us_df['text'] = us_df['text'].apply(clean_text)
    
    
    us_df['sentiment'] = us_df['text'].apply(lambda x: sid.polarity_scores(x))
    
    return us_df

#join census data
def get_census(coords):
    url='https://geo.fcc.gov/api/census/area?lat={}&lon={}&format=json'.format(coords[0],coords[1])
    res = requests.get(url)
    if res.json()['results']==[]:
        return None
    else:
        return res.json()['results'][0]['block_fips'][:-4]

def census_df(df):
    census = []
    count=0
    req_count=0
    while len(census)< df.shape[0]:
        census.append(get_census(df['coords'][count]))
        if req_count % 50 == 0:
            print("Just spacing out my calls a bit")
            time.sleep(2*60)
        if req_count > 998:
            print("sleep time")
            time.sleep(60*60)

    df['census']=census
    return df


if __name__ == "__main__":

    client = MongoClient()
    db = client['capstone']

    sid = SentimentIntensityAnalyzer() 
    
    #replace these with your collection data 
    healthy_df = pull_geodata('healthy') 
    us_healthy = prep_twitter_df(healthy_df)
    census_healthy = census_df(us_healthy)
    