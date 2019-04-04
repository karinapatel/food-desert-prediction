from model_prep import prep_data
from sklearn.model_selection import train_test_split,cross_val_score
from sklearn.ensemble import RandomForestClassifier,GradientBoostingClassifier
from sklearn.metrics import roc_auc_score, f1_score, accuracy_score,recall_score,precision_score,roc_curve
from sklearn.model_selection import GridSearchCV
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

#general modeling function:
def my_model(model_name):
    #which model I want to run
    model = model_name
    #fit the data on the model passed in
    model.fit(df_train,y_train)
    
    #training stats
    print("TRAIN")
    print("ROC_AUC score: ", cross_val_score(LogisticRegression(),df_train,y_train,cv=5,scoring='roc_auc').mean())
    print("Accuracy score: ", cross_val_score(LogisticRegression(),df_train,y_train,cv=5).mean())
    print("f1 score: ", cross_val_score(LogisticRegression(),df_train,y_train,cv=5,scoring='f1').mean())

    #predict on the fit model
    y_pred = model.predict(df_test)

    #testing stats
    print("TEST")
    print("ROC_AUC score: ", roc_auc_score(y_test,y_pred))
    print("Accuracy score: ", accuracy_score(y_test,y_pred))
    print("f1 score: ", f1_score(y_test,y_pred))
    print("recall score: ", recall_score(y_test,y_pred))
    print("precision score: ", precision_score(y_test,y_pred))

def plot_ROC(modelname,model,X_train,y_train,X_test,y_test,path_to_img):
    #fit and calc probas    
    model.fit(X_train,y_train)
    y_pred = model.predict(X_test)
    y_predproba = model.predict_proba(X_test)
    fpr,tpr,thresholds=roc_curve(y_test.values,y_predproba[:,1])
    auc = roc_auc_score(y_test,y_pred)
    #plot ROC
    fig,ax = plt.subplots(1,1,figsize=(9,7))
    ax.plot(fpr,tpr,label='{}: {}'.format(modelname,auc),marker='*', color='green')
    ax.plot([0,1],[0,1], 'k:')
    ax.set_xlabel("False Positive Rate (FPR)")
    ax.set_ylabel("True Positive Rate (TPR)")
    ax.set_title("ROC Curve for {} Model".format(modelname))
    ax.legend(loc='lower right')
    
    #save to path
    fig.savefig(path_to_img)



if __name__ == "__main__":
    #call prep_data for form my training and testing transformed datasets
    df_train,y_train,df_test,y_test = prep_data()

    #REMEMBER: import  modules for any models you are using below 
    
    # #model logistic
    # print("Logistic: ")
    # my_model(LogisticRegression(penalty='l1'))

    # #model SVM
    # print("SVM")
    # my_model(LinearSVC(penalty='l2',loss='hinge'))
    
    # #model KNN
    # print("KNN")
    # my_model(KNeighborsClassifier(n_neighbors=5))
    
    # #model Decision Trees
    # print("Decision Trees")
    # my_model(DecisionTreeClassifier())

    # #model RF
    # print("RandomForest")
    # my_model(RandomForestClassifier(max_depth= None,max_features='sqrt',n_estimators=400))
    
    
    #model GB
    print("GradientBoosting")
    model = GradientBoostingClassifier(criterion='friedman_mse', init=None,
            learning_rate=0.1, loss='deviance', max_depth=5,
            max_features=20, max_leaf_nodes=None,
            min_impurity_decrease=0.0, min_impurity_split=None,
            min_samples_leaf=13, min_samples_split=2,
            min_weight_fraction_leaf=0.0, n_estimators=100,
            presort='auto', random_state=None, subsample=1.0, verbose=0,
            warm_start=False)
    my_model(model)

    plot_ROC("Gradient Boosting",model,df_train,y_train,df_test,y_test,"images/test_ROC.png")


