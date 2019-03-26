from cleaning_script import prep_data
from sklearn.model_selection import train_test_split,cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, f1_score, accuracy_score

#general modeling function:
def my_model(model_name):
    #which model I want to run
    model = model_name
    #fit the data on the model passed in
    model.fit(df_train,y_train)
    
    #training stats
    print("TRAIN on {}".format(model_name[:-2]))
    print("ROC_AUC score: ", cross_val_score(LogisticRegression(),df_train,y_train,cv=5,scoring='roc_auc').mean())
    print("Accuracy score: ", cross_val_score(LogisticRegression(),df_train,y_train,cv=5).mean())
    print("f1 score: ", cross_val_score(LogisticRegression(),df_train,y_train,cv=5,scoring='f1').mean())

    #predict on the fit model
    y_pred = model.predict(df_test)

    #testing stats
    print("TEST on {}".format(model_name[:-2]))
    print("ROC_AUC score: ", roc_auc_score(y_test,y_pred))
    print("Accuracy score: ", accuracy_score(y_test,y_pred))
    print("f1 score: ", f1_score(y_test,y_pred))


if __name__ == "__main__":
    #call prep_data for form my training and testing transformed datasets
    df_train,y_train,df_test,y_test= prep_data()

    #REMEMBER: import  modules for any models you are using below 
    
    #model logistic
    print("Logistic: ")
    my_model(LogisticRegression())

    #model RF
    print("RandomForest")
    my_model(RandomForestClassifier())

    #any other models: