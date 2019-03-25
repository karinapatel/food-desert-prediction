import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

def clean(df):
    df.fillna(df.mean(),inplace=True)
    data1=df[['TEETHLOST_CrudePrev','STROKE_CrudePrev','PHLTH_CrudePrev','OBESITY_CrudePrev','MHLTH_CrudePrev','LPA_CrudePrev','KIDNEY_CrudePrev','DENTAL_CrudePrev','DIABETES_CrudePrev','CSMOKING_CrudePrev','COREW_CrudePrev','COPD_CrudePrev','CHOLSCREEN_CrudePrev','CASTHMA_CrudePrev','ACCESS2_CrudePrev','PovertyRate','TractSNAP']]
    return data1

def prep_data():

    food_desert = pd.ExcelFile('data/DataDownload2015.xlsx')

    desert_data = food_desert.parse(2)
    desert_data.set_index('CensusTract', inplace=True)

    behav = pd.read_csv('data/500_Cities__Census_Tract-level_Data__GIS_Friendly_Format___2018_release.csv',)
    behav.set_index('TractFIPS', inplace=True)

    merge1 = behav.merge(desert_data, how='left', left_index=True, right_index=True)
    merge1['LILATracts_halfAnd10'].fillna(0,inplace=True)

    y=merge1.pop('LILATracts_halfAnd10')
    X=merge1
    #train test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)

    df_train = clean(X_train)
    df_test = clean(X_test)

    return df_train,y_train,df_test,y_test