import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
from http.client import HTTPSConnection #note the S
import pandas as pd
import numpy as np

def state_scrape():

    #url with the state fips, abbreviation, and name of state
    URL="https://www.mcc.co.mercer.pa.us/dps/state_fips_code_listing.htm"
    content = requests.get(URL).content
    #pull with BS
    soup = BeautifulSoup(content, "html.parser")

    #get table values into 3 lists: abbreviations, fips, and name
    values=[]
    row=[]
    for ind,val in enumerate(soup.table.find_all('td')[6:],1):
        if val.text != '\xa0':
            row.append(val.text)
    abbr=[]
    fips=[]
    name=[]
    for ind in range(0,165,3):
        abbr.append(row[ind])
        fips.append(row[ind+1])
        name.append(row[ind+2])
    np.array([abbr,fips,name])

    #put the results into a dataframe
    state_data = pd.DataFrame(np.array([abbr,fips,name]).T,columns=['abbreviation','FIPS','name'])

    return state_data

if __name__ == "__main__":
    state_data = state_scrape()
    state_data.to_csv('../data/state_data.csv')


