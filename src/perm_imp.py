from sklearn.metrics import roc_auc_score, f1_score, accuracy_score,recall_score,precision_score,roc_curve
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
import matplotlib.pylab as plt
from sklearn.ensemble import RandomForestClassifier,GradientBoostingClassifier

def permutation_importance(model, X_test, y_test, scorer=f1_score):
    ''' Calculates permutation feature importance for a fitted model
    
    Parameters
    ----------
    model: anything with a predict() method
    X_test, y_test: numpy arrays of data
        unseen by model
    scorer: function. Should be a "higher is better" scoring function,
        meaning that if you want to use an error metric, you should
        multiply it by -1 first.
        ex: >> neg_mse = lambda y1, y2: -mean_squared_error(y1, y2)
            >> permutation_importance(mod, X, y, scorer=neg_mse)
    
    Returns
    -------
    feat_importances: numpy array of permutation importance
        for each feature
    
    '''
    
    feat_importances = np.zeros(X_test.shape[1])
    test_score = scorer(model.predict(X_test), y_test)
    for i in range(X_test.shape[1]):
        X_test_shuffled = shuffle_column(X_test, i)
        test_score_permuted = scorer(y_test, model.predict(X_test_shuffled))
        feat_importances[i] = test_score - test_score_permuted
    return feat_importances

def shuffle_column(X, feature_index):
    ''' 
    Parameters
    ----------
    X: numpy array
    feature_index: int
    
    Returns
    -------
    X_new: numpy array
    
    Returns a new array identical to X but
    with all the values in column feature_index
    shuffled
    '''   
    
    X_new = X.copy()
    np.random.shuffle(X_new[:,feature_index])
    return X_new

## Plot of feature importances
def plot_feat_import(f_imps, names, n):
    sorts = np.argsort(f_imps)
    
    last_x = f_imps[sorts[-n:-1]]
    last_x_names = names[sorts[-n:-1]]

    idx = np.arange(len(names))

    plt.barh(idx[-n:-1], last_x, align='center')
    plt.yticks(idx[-n:-1], last_x_names)

    plt.title("Permutation Importances in Gradient Boosting")
    plt.xlabel('Relative Importance of Feature')
    plt.ylabel('Feature Name')
    plt.savefig("feature_importances.jpg")
    plt.show()