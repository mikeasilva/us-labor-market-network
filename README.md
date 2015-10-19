# U.S. Labor Market Network

## Introduction
This project examines U.S. worker flow data to identify labor markets.  Through the chosen methodology 51 labor markets were discovered.

## Data Source
The [CTPP data product](http://ctpp.transportation.org/Pages/5-Year-Data.aspx) based on 2006 - 2010 5-year American Community Survey (ACS) Data was used in this project.  I made a custom download request of table A302100 - Total Workers (1) (Workers 16 years and over).  I selected all U.S. Counties as the RESIDENCE and WORKPLACE through the Beyond 2020 interface, and deselected the states (default setting).  Anyone can access the raw CTPP data through [the original download request](http://dataa.beyond2020.com/BulkDownload/BulkDownloadFiles/Job_4393.csv) or [my Google drive backup](https://googledrive.com/host/0B9jKAdYAFCl3bk9jODNteXhYbFk/Job_4393.csv).

## Data Manipulation
The raw data provided the nodes and edges for the analysis.  The number of workers were used as a weighting varaible for each edge.  The data was processed using Python.  I developed the script to filter out data based on three criteria:  
1.  The option to filter if the node loops back on itself;  
2.  If the number of workers (edge weight) was under a threshold;  
3.  If the data was too unreliable (meaning the margin of error to estimate ratio over a threshold).  

Through a trial and error process I settled on parameters for the three criteria that left data for 97% of the counties in the orignal set and 6% of the edges.  I have left two other cases using alternative parameters.  I used the NetworkX library to create the graph and then exported it as a graphml file. 

## Network Clustering
I used Gephi to analyze the graph and discover the clusters.  I used the modularity community detection algorithm.  To make the results reproducable I unchecked the "Randomize" option but left all other options with their default settings as shown here:

![Modularity Settings](modularity-settings.png)

This resulted in 51 communities being discovered.