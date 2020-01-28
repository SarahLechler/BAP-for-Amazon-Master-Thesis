# Import Python 3's print function and division
from __future__ import print_function, division

# Import GDAL, NumPy, and matplotlib
from osgeo import gdal, gdal_array
import numpy as np
import matplotlib.pyplot as plt
from sklearn import tree
import create_yearly_time_series as yts
import graphviz

"""
cluster algorithm:
kmeans(?)
SOM
decision tree and export the model to file (svg/png) --> how is it splitting the data
"""


def runDT(X, y, index):
    print('Creating classifier')
    # Initialize our model with 500 trees
    clf = tree.DecisionTreeClassifier()

    # Fit our model to training data
    clf = clf.fit(X, y)

    r = tree.export_graphviz(clf, out_file=index+"tree.dot")