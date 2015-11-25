# -*- coding: utf-8 -*-

import pandas as pd
import networkx as nx

# Data Management Parameters
estimate_over_moe_threshold = 0.5
worker_threshold = 100
dont_link_to_self = True

# Read in data
df = pd.read_csv('Job_4393.csv', low_memory=False, skiprows=2, thousands=',')

# Change 'Workers 16 and Over' to numeric
df['Workers 16 and Over'] = pd.to_numeric(df['Workers 16 and Over'])

# Only pull the first 4 columns of data
df = df.iloc[:,0:4]

# Quickly get the count of the nodes and edges
nodes_before = len(pd.DataFrame(pd.concat([df['RESIDENCE'], df['WORKPLACE']])).drop_duplicates())
edges_before = len(df)

# Reshape for long to wide
left = df[df['Output']=='Estimate'].drop('Output', 1).rename(columns={'Workers 16 and Over':'Estimate'})
right = df[df['Output']=='Margin of Error'].drop('Output', 1).rename(columns={'Workers 16 and Over':'Margin of Error'})

df = pd.merge(left, right, on=['RESIDENCE','WORKPLACE'])

# Eliminate questionable data
df['MOE over EST'] = df['Margin of Error'] / df['Estimate']
df = df[df['MOE over EST'] <= estimate_over_moe_threshold]

# Drop unneded columns
df = df.drop(['Margin of Error', 'MOE over EST'], 1)

# Eliminate small figures
df = df[df['Estimate'] >= worker_threshold]

# Eliminate links to self if needed
if dont_link_to_self:
    df = df[df['RESIDENCE'] != df['WORKPLACE']]
    
# Create a nodes data frame
nodes = pd.DataFrame(pd.concat([df['RESIDENCE'], df['WORKPLACE']])).drop_duplicates().rename(columns={0:'County'})
nodes= nodes.reset_index(drop=True)
nodes['Id'] = nodes.index

# Pull in the FIPS code data frames
# This is a bit of a hack as I tweaked ACS Geography data so that the county names will match up
fips = pd.read_csv('fips.csv', low_memory=False,  converters={'FIPS': str})
nodes = pd.merge(nodes, fips)

# Add the source
df = pd.merge(df, nodes, left_on='RESIDENCE', right_on='County')
df = df.drop(['County','FIPS'], 1).rename(columns={'Id':'Source'})

# Add the target
df = pd.merge(df, nodes, left_on='WORKPLACE', right_on='County')
df = df.drop(['County','FIPS'], 1).rename(columns={'Id':'Target'})

# Get the update on the nodes and edges counts
nodes_after = len(nodes)
edges_after = len(df)

# Calculate Percentages
nodes_percent = nodes_after * 100 / nodes_before
edges_percent = edges_after * 100 / edges_before

# Print out stats about the nodes and edges counts
print('Includes '+str(nodes_after)+' of the '+str(nodes_before)+' nodes ('+str(nodes_percent)+'%)')
print('Includes '+str(edges_after)+' of the '+str(edges_before)+' edges ('+str(edges_percent)+'%)')

# Create the graph
G = nx.DiGraph()

# Add in the edges
for row in df.iterrows():
    G.add_edge(row[1][3], row[1][4], weight=row[1][2])

labels = nodes[['Id','County']].to_dict()
labels = labels['County']

fips = nodes[['Id','FIPS']].to_dict()
fips = fips['FIPS']

nx.set_node_attributes(G, 'label', labels)
nx.set_node_attributes(G, 'fips', fips)

# Write the graph to files
nx.write_graphml(G,'U.S. Labor Market.graphml')
nx.write_weighted_edgelist(G,'U.S. Labor Market.edgelist')