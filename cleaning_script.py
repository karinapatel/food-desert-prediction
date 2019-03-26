import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

#this helper function should take in either X_train or X_test and format it in a way that prepares it for model fitting
def clean(df):
    #very few nulls in the data set -- filling them with the column mean
    df.fillna(df.mean(),inplace=True)
    #subset of data features based on EDA and correlation analysis
    data1=df[['TEETHLOST_CrudePrev','STROKE_CrudePrev','PHLTH_CrudePrev','OBESITY_CrudePrev','MHLTH_CrudePrev','LPA_CrudePrev','KIDNEY_CrudePrev','DENTAL_CrudePrev','DIABETES_CrudePrev','CSMOKING_CrudePrev','COREW_CrudePrev','COPD_CrudePrev','CHOLSCREEN_CrudePrev','CASTHMA_CrudePrev','ACCESS2_CrudePrev','PovertyRate','TractSNAP']]
    return data1

#prepping data for modeling
def prep_data():

    #food desert data + poverty rates + SNAP counts
    food_desert = pd.ExcelFile('data/DataDownload2015.xlsx')

    #just want  data, other sheets in the excel workbook are a readME and variable description
    desert_data = food_desert.parse(2)
    #set index to prepare for merging data sets
    desert_data.set_index('CensusTract', inplace=True)

    #behavior and health data 
    behav = pd.read_csv('data/500_Cities__Census_Tract-level_Data__GIS_Friendly_Format___2018_release.csv',)
    #setting index to the same feature as desert_data
    behav.set_index('TractFIPS', inplace=True)

    #merge the data sets tp create our large dataset
    merge1 = behav.merge(desert_data, how='left', left_index=True, right_index=True)
    #there are a total of 4 nulls out of all rows (over 28000) so I filled these with a non_food desert label
    merge1['LILATracts_halfAnd10'].fillna(0,inplace=True)

    #ready for splitting data

    #target food desert classification
    y=merge1.pop('LILATracts_halfAnd10')
    #feature matrix
    X=merge1
    #train test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)

    #perform cleaning on each dataset independently to prep for model fit and predict
    df_train = clean(X_train)
    df_test = clean(X_test)

    #return training and testing sets
    return df_train,y_train,df_test,y_test