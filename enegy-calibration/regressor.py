import pandas as pd
import numpy as np
from sklearn import linear_model, metrics
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, AdaBoostRegressor, ExtraTreesRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.tree import export_graphviz
from scipy.optimize import nnls

data = pd.read_csv('data-40.csv')

x = data.iloc[:,0:5]
y = data.iloc[:,5:6]

print(x,y)

x_train, x_test, y_train, y_test = train_test_split(x, y)

linearRegressor = LinearRegression(positive=True)

regressors = [linearRegressor]

for regressor in regressors:
    regressor.fit(x_train, y_train)
    y_pred = regressor.predict(x_test)
    print('Mean Absolute Error with ', regressor, ' is: ', metrics.mean_absolute_error(y_test, y_pred))
    print('Mean Squared Error with ', regressor, ' is: ', metrics.mean_squared_error(y_test, y_pred))
    print('Root Mean Squared Error with ', regressor, ' is: ', np.sqrt(metrics.mean_squared_error(y_test, y_pred)))
    print("Coefficients: ", list(regressor.coef_))

print("Coefficients using NNLS: ", nnls(np.array(x), y['energy'].values))