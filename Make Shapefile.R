library(rgdal)
library(dplyr)
shape <- readOGR(dsn = 'E:/GIS/tl_2015_us_county', layer = 'tl_2015_us_county')
shape@data <- shape@data %>%
  mutate(fips = paste0(STATEFP,COUNTYFP))

temp <- read.csv('Regionalized U.S. Counties.csv', nrows=1)
shape@data <- read.csv('Regionalized U.S. Counties.csv', colClasses = rep('character', length(temp))) %>%
  mutate(Area.Name = as.factor(Area.Name)) %>%
  merge(shape@data, ., all.x=TRUE)

writeOGR(shape, dsn = 'E:/GIS/labornetworks', layer ='labornetworks', driver = 'ESRI Shapefile')
