# -*- coding: utf-8 -*-
"""
This script fills in the modularity class holes.  The way it determines which
modularity class to use it uses the raw CTPP data and determines which area
(or modularity class) has the most links with the county.
"""
# Import the libraries we need
import pandas as pd
import numpy as np

# Read in the 2015 Census Tiger Lines County shapefile
df = pd.read_csv('tl_2015_us_county.csv', low_memory=False, dtype={'fips': 'S5'})
# Subset the data, rename the columns and change variable types (data wrangling)
df = df[['fips', 'NAMELSAD','INTPTLAT','INTPTLON']]
df = df.rename(columns={'fips':'fips', 'NAMELSAD':'County', 'INTPTLAT':'Latitude', 'INTPTLON':'Longitude'}).reindex()
df.Latitude = df.Latitude.astype(float)
df.Longitude = df.Longitude.astype(float)

# Add in Wade Hampton County AK which is not present in the Tiger Files
df.loc[len(df)+1]=['02270','Wade Hampton County', 62.0826229, -165.428791]

# Read in the Gephi output
nodes = pd.read_csv('U.S. Labor Market [Nodes].csv', low_memory=False,  converters={'fips': str})
nodes = nodes[['fips','Modularity Class']]

# Merge the two data frames so we can predict the modularity class as a 
# function of latitude and longitude
df = pd.merge(df, nodes, how='left')

# Find the records without a modularity class
holes = df[df['Modularity Class'].isnull()]

# Read in data
ctpp = pd.read_csv('Job_4393.csv', low_memory=False, skiprows=2, thousands=',')
ctpp = ctpp[ctpp['Output']=='Estimate'].drop('Output', 1)
fips = pd.read_csv('fips.csv', low_memory=False,  converters={'FIPS': str})

# Change 'Workers 16 and Over' to numeric
ctpp['Workers 16 and Over'] = pd.to_numeric(ctpp['Workers 16 and Over'])
ctpp = pd.merge(ctpp, fips, left_on='RESIDENCE', right_on='County', how='left')
ctpp = pd.merge(ctpp, nodes, left_on='FIPS', right_on='fips', how='left')
ctpp = pd.merge(ctpp, fips, left_on='WORKPLACE', right_on='County', how='left')
ctpp = pd.merge(ctpp, nodes, left_on='FIPS_y', right_on='fips', how='left')

for f in holes.fips:
    x = ctpp[ctpp.FIPS_x == f]
    x = x.groupby('Modularity Class_y')['Workers 16 and Over'].agg([np.sum])
    x = x.reset_index().rename(columns={'Modularity Class_y':'Modularity Class'})
    y = ctpp[ctpp.FIPS_y == f]
    y = y.groupby('Modularity Class_x')['Workers 16 and Over'].agg([np.sum])
    y = y.reset_index().rename(columns={'Modularity Class_x':'Modularity Class'})
    filler = x.append(y)
    filler = filler.groupby('Modularity Class')['sum'].agg([np.sum])
    filler = filler.reset_index()
    filler = filler.sort_values(by='sum', ascending=False)
    if len(filler.index) > 0:
        mc = filler.iloc[0]['Modularity Class']
        df['Modularity Class'][df.fips==f] = mc
    
# Write the output as a csv file
df.to_csv('Regionalized U.S. Counties.csv', index=False)