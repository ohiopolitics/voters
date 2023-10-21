#%%
# IMPORTS
import altair as alt
import numpy as np
import pandas as pd
import pendulum as p
from sklearn import metrics
from sklearn import metrics
from sklearn.ensemble           import RandomForestClassifier
from sklearn.metrics            import accuracy_score
from sklearn.model_selection    import train_test_split

df = pd.read_csv("sample.csv")

df.info()

p.parse(df["date_of_birth"].str.slice(0,10)[1], strict=False)

df\
    .assign(date_of_birth = lambda x: x["date_of_birth"].str.slice(0,10))\
    # .assign()

# #%%
# X_pred = dat.drop(columns = ['house_income'])   # SET FILTERED VARIABLES
# y_pred = dat['house_income']
# X_pred=X_pred.astype('int')
# y_pred=y_pred.astype('int')

# X_train, X_test, y_train, y_test = train_test_split(X_pred,y_pred,test_size=.26,random_state = 22)    # SPLIT VARIABLES

# clf = RandomForestClassifier(random_state=10).fit(X_train, y_train)  # CREATE MODEL WITH TRAINING DATA

# y_pred = clf.predict(X_test)    # TEST MODEL AND REPORT ACCURACY
# score = accuracy_score(y_test, y_pred)
# print(score)

# #%%
# # GIVE FEATURE IMPORTANCE
# feature_df = pd.DataFrame(
#     {'features': X_train.columns,
#     'importance': clf.feature_importances_})

# best_features = feature_df.sort_values(['importance'],ascending = False).head(6).reset_index(drop=True)

# best_features['importance'] = (round(best_features['importance']*100,2)).astype(str) + ' %'

# # print(best_features.to_markdown())

# metrics.plot_roc_curve(clf,X_test,y_test)
