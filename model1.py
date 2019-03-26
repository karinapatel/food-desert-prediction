from cleaning_script import prep_data
from sklearn.model_selection import train_test_split,cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, f1_score, accuracy_score

#modeling:
def my_model(model_name):
    model = model_name
    model.fit(df_train,y_train)
    
    print("TRAIN on {}".format(model_name[:-2]))
    print("ROC_AUC score: ", cross_val_score(LogisticRegression(),df_train,y_train,cv=5,scoring='roc_auc').mean())
    print("Accuracy score: ", cross_val_score(LogisticRegression(),df_train,y_train,cv=5).mean())
    print("f1 score: ", cross_val_score(LogisticRegression(),df_train,y_train,cv=5,scoring='f1').mean())

    y_pred = model.predict(df_test)

    print("TEST on {}".format(model_name[:-2]))
    print("ROC_AUC score: ", roc_auc_score(y_test,y_pred))
    print("Accuracy score: ", accuracy_score(y_test,y_pred))
    print("f1 score: ", f1_score(y_test,y_pred))


    # #logistic regression
    #model_log = LogisticRegression()

    #print("TRAIN")
    #print("ROC_AUC Logistic: ", cross_val_score(LogisticRegression(),df,y_train,cv=5,scoring='roc_auc').mean())
    #print("Accuracy Logistic: ", cross_val_score(LogisticRegression(),df,y_train,cv=5).mean())
    #print("f1 Logistic: ", cross_val_score(LogisticRegression(),df,y_train,cv=5,scoring='f1').mean())

    # model_log.fit(df_train,y_train)

    # y_pred = model_rf.predict(df_test)

    # print("TEST")
    # print("ROC_AUC Logistic: ", roc_auc_score(y_test,y_pred))
    # print("Accuracy Logistic: ", accuracy_score(y_test,y_pred))
    # print("f1 Logistic: ", f1_score(y_test,y_pred))

    # #random forest
    # model_rf = RandomForestClassifier()

    #print("TRAIN")
    #print("ROC_AUC RF: ", cross_val_score(RandomForestClassifier(),df,y_train,cv=5,scoring='roc_auc').mean())
    #print("Accuracy RF: ", cross_val_score(RandomForestClassifier(),df,y_train,cv=5).mean())
    #print("f1 RF: ", cross_val_score(RandomForestClassifier(),df,y_train,cv=5,scoring='f1').mean())

    # model_rf.fit(df,y_train)
    # y_pred = model_rf.predict(df_test)

    # print("TEST")
    # print("ROC_AUC RF: ", roc_auc_score(y_test,y_pred))
    # print("Accuracy RF: ", accuracy_score(y_test,y_pred))
    # print("f1 RF: ", f1_score(y_test,y_pred))

if __name__ == "__main__":
    df_train,y_train,df_test,y_test= prep_data()
    print("Logistic: ")
    my_model(LogisticRegression())

    print("RandomForest")
    my_model(RandomForest())


