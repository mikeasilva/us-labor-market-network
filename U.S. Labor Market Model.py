# -*- coding: utf-8 -*-
"""
This script develops an ensemble classifier model.  It takes output from Gephi
which breaks out counties into modularity classes and prediects these classes 
based off of lattitude and longitude.

Once the model is developed it classifies all counties in the United States,
and renames the class after the largest city within the region.  A CSV with
all counties and their region is produced for mapping.
"""
# Import the libraries we need
import pandas as pd
import numpy as np
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier, BaggingClassifier, ExtraTreesClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.cross_validation import train_test_split

# Make the results reproducible
np.random.seed(42) # because the answer to everything is 42

# Read in the 2010 Census list of counties
df = pd.read_csv('DEC_10_SF1_G001_with_ann.csv', low_memory=False)
# Since the second row has the variable names I want to use let's swap them out
old_names = list(df.columns.values)
new_names = list(df[:1].values[0])
names = dict(zip(old_names, new_names))
df = df.drop(df.index[[0]]).rename(columns=names).reindex()

# Subset the data, rename the columns and change variable types (data wrangling)
df = df[['Id2', 'Geography','AREA CHARACTERISTICS - Internal Point (Latitude)','AREA CHARACTERISTICS - Internal Point (Longitude)']]
df = df.rename(columns={'Id2':'fips', 'Geography':'County', 'AREA CHARACTERISTICS - Internal Point (Latitude)':'Latitude', 'AREA CHARACTERISTICS - Internal Point (Longitude)':'Longitude'}).reindex()
df.Latitude = df.Latitude.astype(float)
df.Longitude = df.Longitude.astype(float)

# Read in the Gephi output
nodes = pd.read_csv('U.S. Labor Market [Nodes].csv', low_memory=False,  converters={'fips': str})
nodes = nodes[['fips','Modularity Class']]

# Merge the two data frames so we can predict the modularity class as a 
# function of latitude and longitude
merged = pd.merge(df, nodes)
# Break them out into independent and dependant variables
x=pd.DataFrame(merged, columns=['Latitude', 'Longitude'])
y=pd.Series(merged['Modularity Class'])
# Create a training and test set
x_train, x_test, y_train, y_test = train_test_split(x, y, random_state=0)

"""
Create the Ensemble Model

The individual models should print out the following scores:

+===============+================+
| Model Name    | Model Score    |
+===============+================+
| Random Forest | 0.884810126582 |
| Extra Trees   | 0.849367088608 |
| SVM           | 0.855696202532 |
| Bagging       | 0.905063291139 |
| Decision Tree | 0.870886075949 |
+===============+================+
"""
#  Model Number 1 - Random Forest
rf = RandomForestClassifier(n_estimators=10, max_depth=None, min_samples_split=1, random_state=0)
rf_model = rf.fit(x_train, y_train)
rf_score = rf_model.score(x_test, y_test)
print(rf_score)

#  Model Number 2 - Extra Trees
et = ExtraTreesClassifier(n_estimators = 10, criterion = 'gini')
et_model = et.fit(x_train, y_train)
et_score = et_model.score(x_test, y_test)
print(et_score)

#  Model Number 3 - SVM
classifier = svm.SVC(kernel='linear')
svm_model = classifier.fit(x_train, y_train)
svm_score = svm_model.score(x_test, y_test)
print(svm_score)

#  Model Number 4 - Bagging
bag = BaggingClassifier(KNeighborsClassifier())
bag_model = bag.fit(x_train, y_train)
bag_score = bag_model.score(x_test, y_test)
print(bag_score)

#  Model Number 5 - Decision Trees
dt = DecisionTreeClassifier(max_depth=None, min_samples_split=1, random_state=0)
dt_model = dt.fit(x_train, y_train)
dt_score = dt_model.score(x_test, y_test)
print(dt_score)                    

# Predict the Modularity class based on the latitude and longitude for all the
# counties in the US
test=pd.DataFrame(df, columns=['Latitude', 'Longitude'])

# Store the results
results = pd.DataFrame(df, columns=['fips'])
results['bag'] = df['bag'] = bag.predict(test)
results['rf'] = df['rf'] = rf.predict(test)
results['svm'] = df['svm'] = classifier.predict(test)
results['et'] = df['et'] = et.predict(test)
results['dt'] = df['dt'] = dt.predict(test)

# Stack the models using majority rule to determine the classification
vote = results.mode(axis = 1)
df['pred'] = vote[0]

# Read in the 2010 Census Incorporated Places
places = pd.read_csv('2010-incorporated-places.csv', low_memory=False)

# Again the first row contains the variable names
old_names = list(places.columns.values)
new_names = list(places[:1].values[0])
names = dict(zip(old_names, new_names))
places = places.drop(places.index[[0]]).rename(columns=names).reindex()

# Data wrangling of the places
places = places[['Id2', 'Geography','AREA CHARACTERISTICS - Internal Point (Latitude)','AREA CHARACTERISTICS - Internal Point (Longitude)', 'AREA CHARACTERISTICS - Population Count (100%)']]
places = places.rename(columns={'Id2':'fips', 'Geography':'Geography', 'AREA CHARACTERISTICS - Internal Point (Latitude)':'Latitude', 'AREA CHARACTERISTICS - Internal Point (Longitude)':'Longitude', 'AREA CHARACTERISTICS - Population Count (100%)':'Population'}).reindex()
places.Latitude = places.Latitude.astype(float)
places.Longitude = places.Longitude.astype(float)
places.Population = places.Population.convert_objects(convert_numeric=True)

# Drop the CDP's and the "Balance of" locations
places = places[places.Geography.str.contains('CDP') == False]
places = places[places.Geography.str.contains('balance') == False]

# Classify the places
places_test=pd.DataFrame(places, columns=['Latitude', 'Longitude'])
places_results = pd.DataFrame(places, columns=[['fips']])
places_results['bag'] = bag.predict(places_test)
places_results['rf'] = rf.predict(places_test)
places_results['svm'] = classifier.predict(places_test)
places_results['et'] = et.predict(places_test)
places_results['dt'] = dt.predict(places_test)

# Stack the models using majority rule
places_vote = places_results.mode(axis = 1)
places_results['pred'] = places_vote[0]

# Merge in the population and geography name
temp = places[['fips','Population','Geography']]
places_results = pd.merge(places_results, temp)

# Get the largest city
names = pd.DataFrame(places_results.groupby(['pred'])['Population'].max())
names['pred'] = names.index
names = pd.merge(names, places_results)
names = names[['pred','Geography']]

# Clean up the geography name
names.Geography = names.Geography.str.replace(' city,', ',')
names.Geography = names.Geography.str.replace(' urban county,', ',')
names.Geography = names.Geography.str.replace(' zona urbana,', ',')
names.Geography = names.Geography.str.replace(' municipality,', ',')
names = names.rename(columns={'Geography':'Area Name'})

# Merge in the named region into the data frame
df = pd.merge(df, names)

# Write the output as a csv file
df.to_csv('Regionalized U.S. Counties.csv')