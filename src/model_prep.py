import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import ast

#this helper function should take in either X_train or X_test and format it in a way that prepares it for model fitting
def clean(df):
    #very few nulls in the data set -- filling them with the column mean
    df.fillna(df.mean(),inplace=True)
    #subset of data features based on EDA and correlation analysis
    data1=df[['TEETHLOST_CrudePrev','STROKE_CrudePrev','PHLTH_CrudePrev','OBESITY_CrudePrev','MHLTH_CrudePrev','LPA_CrudePrev','KIDNEY_CrudePrev','DENTAL_CrudePrev','DIABETES_CrudePrev','CSMOKING_CrudePrev','COREW_CrudePrev','COPD_CrudePrev','CHOLSCREEN_CrudePrev','CASTHMA_CrudePrev','ACCESS2_CrudePrev','PovertyRate','TractSNAP','comp_healthy','comp_unhealthy','comp_grocery','comp_ff','Population2010','PCTGQTRS','HUNVFlag']]
    #normalized features based on total population
    data1['TractLOWI']=df['TractLOWI']/df['Population2010']
    data1['TractKids']=df['TractKids']/df['Population2010']
    data1['TractSeniors']=df['TractSeniors']/df['Population2010']
    data1['TractWhite']=df['TractWhite']/df['Population2010']
    data1['TractBlack']=df['TractBlack']/df['Population2010']
    data1['TractAsian']=df['TractAsian']/df['Population2010']
    data1['TractNHOPI']=df['TractNHOPI']/df['Population2010']
    data1['TractAIAN']=df['TractAIAN']/df['Population2010']
    data1['TractOMultir']=df['TractOMultir']/df['Population2010']
    data1['TractHispanic']=df['TractHispanic']/df['Population2010']
    data1['TractHUNV']=df['TractHUNV']/df['Population2010']
    data1['TractSNAP']=df['TractSNAP']/df['Population2010']
    #return cleaned df
    return data1

#prepping data for modeling
def prep_data():
    #food desert data + poverty rates + SNAP counts
    food_desert = pd.ExcelFile('data/food_desert_data.xlsx')

    #just want  data, other sheets in the excel workbook are a readME and variable description
    desert_data = food_desert.parse(2)
    #account for the dropped 0 at the beginning of some census tracts by python default
    desert_data['CensusTract']=desert_data['CensusTract'].apply(lambda x: "0"+str(x) if len(str(x))==10 else str(x)) 
    #set index to prepare for merging data sets
    desert_data.set_index('CensusTract', inplace=True)


    #behavior and health data 
    behav = pd.read_csv('data/population_health.csv',)
    #account for the dropped 0 at the beginning of some census tracts by python default
    behav['TractFIPS']=behav['TractFIPS'].apply(lambda x: "0"+str(x) if len(str(x))==10 else str(x)) 
    #setting index to the same feature as desert_data
    behav.set_index('TractFIPS', inplace=True)

    #merge the data sets to create our large dataset
    merge1 = behav.merge(desert_data, how='inner', left_index=True, right_index=True)    

    #ready for splitting data
    #target food desert classification
    y=merge1.pop('LILATracts_halfAnd10')
    #feature matrix
    X=merge1
    #add county column derived from census #
    X['county'] = [i[:5] for i in X.index]
    
    print("Preparing Healthy DF")
    #cleaned mongo data
    healthy_clean=pd.read_csv('data/twitter_mongo/healthy_clean.csv',index_col=0)
    #account for the dropped 0 at the beginning of some census tracts by python default
    healthy_clean['census']=healthy_clean['census'].apply(lambda x: "0"+str(x) if len(str(x))==10 else str(x)) 
    #add county and pull sentiment score out as comp
    healthy_clean['county'] = healthy_clean['census'].apply(lambda x: x[:5])
    healthy_clean['sentiment']=healthy_clean['sentiment'].apply(ast.literal_eval)
    healthy_clean['comp_healthy']=healthy_clean['sentiment'].apply(lambda x: x['compound'])
    #get avg sentiment by county
    county_sent_healthy = healthy_clean.groupby('county').mean()['comp_healthy']
    county_sent_healthy = county_sent_healthy.reset_index()
    
    print("Preparing Unealthy DF")
    #cleaned mongo data
    unhealthy_clean=pd.read_csv('data/twitter_mongo/unhealthy_clean.csv',index_col=0)
    unhealthy_clean['census']=unhealthy_clean['census'].apply(lambda x: "0"+str(x) if len(str(x))==10 else str(x))
    #there is only 1 entry outside of US: drop it
    unhealthy_clean.dropna(axis=0, inplace=True)
    #get all census tracts as 11 digit integers: 
    unhealthy_clean.census=unhealthy_clean.census.apply(float)
    unhealthy_clean.dropna(axis=0, inplace=True)
    unhealthy_clean.census=unhealthy_clean.census.apply(int)
    #account for the dropped 0 at the beginning of some census tracts by python default
    unhealthy_clean['census']=unhealthy_clean['census'].apply(lambda x: "0"+str(x) if len(str(x))==10 else str(x)) 
    #add county and pull sentiment score out as comp
    unhealthy_clean['county'] = unhealthy_clean['census'].apply(lambda x: x[:5])
    unhealthy_clean['sentiment']=unhealthy_clean['sentiment'].apply(ast.literal_eval)
    unhealthy_clean['comp_unhealthy']=unhealthy_clean['sentiment'].apply(lambda x: x['compound'])
    #get avg sentiment by county
    county_sent_unhealthy = unhealthy_clean.groupby('county').mean()['comp_unhealthy']
    county_sent_unhealthy = county_sent_unhealthy.reset_index()
    
    print("Preparing Grocery DF")
    #cleaned mongo data
    grocery_stores_clean=pd.read_csv('data/twitter_mongo/grocery_stores_clean.csv',index_col=0)
    #account for the dropped 0 at the beginning of some census tracts by python default
    grocery_stores_clean['census']=grocery_stores_clean['census'].apply(lambda x: "0"+str(x) if len(str(x))==10 else str(x)) 
    #add county and pull sentiment score out as comp
    grocery_stores_clean['county'] = grocery_stores_clean['census'].apply(lambda x: x[:5])
    grocery_stores_clean['sentiment']=grocery_stores_clean['sentiment'].apply(ast.literal_eval)
    grocery_stores_clean['comp_grocery']=grocery_stores_clean['sentiment'].apply(lambda x: x['compound'])
    #get avg sentiment by county
    county_sent_grocery = grocery_stores_clean.groupby('county').mean()['comp_grocery']
    county_sent_grocery = county_sent_grocery.reset_index()
 
    print("Preparing FF DF")
    #cleaned mongo data
    ff_stores_clean=pd.read_csv('data/twitter_mongo/ff_stores_clean.csv',index_col=0)
    #account for the dropped 0 at the beginning of some census tracts by python default
    ff_stores_clean['census']=ff_stores_clean['census'].apply(lambda x: "0"+str(x) if len(str(x))==10 else str(x)) 
    #add county and pull sentiment score out as comp
    ff_stores_clean['county'] = ff_stores_clean['census'].apply(lambda x: x[:5])
    ff_stores_clean['sentiment']=ff_stores_clean['sentiment'].apply(ast.literal_eval)
    ff_stores_clean['comp_ff']=ff_stores_clean['sentiment'].apply(lambda x: x['compound'])
    #get avg sentiment by county
    county_sent_ff = ff_stores_clean.groupby('county').mean()['comp_ff']
    county_sent_ff = county_sent_ff.reset_index()
    
    #add all sentiments (healthy, unhealthy, ff, grocery) to X df
    print("Merging county sentiment")
    X1 = pd.merge(X,county_sent_healthy,how='left',left_on='county', right_on='county')
    X2 = pd.merge(X1,county_sent_unhealthy,how='left',left_on='county', right_on='county')
    X3 = pd.merge(X2,county_sent_grocery,how='left',left_on='county', right_on='county')
    X4 = pd.merge(X3,county_sent_ff,how='left',left_on='county', right_on='county')

    #fill nulls with -1
    X4.fillna(-1,inplace=True)

    #train test split
    X_train, X_test, y_train, y_test = train_test_split(X4, y, test_size=0.20, random_state=42)

    #perform cleaning on each dataset independently to prep for model fit and predict
    print("Cleaning train and test DF")
    df_train = clean(X_train)
    df_test = clean(X_test)

    #return training and testing sets
    return df_train,y_train,df_test,y_test