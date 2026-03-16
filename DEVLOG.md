#Development Log
#I want to use this file as a diary(sort of) where I will be writing my thought process, any problems I am encountering etc.
#I already have written some, so I am just transfer them. The first days diary is really short because I didn't have the plan for a development log.

#Day 1- 24/02/2026 
Neither Nordpool nor ENTSOE lets me download historical data for that many years. 
I guess I have to use the EnergiData API. 

#Day 2 - 11/03/2026
I started by using the wind forecast and wind actual data because it has the most important role in Denmark’s energy mix. 
Of course solar, hydro, gas, interconnectors can be used but my first step is to create a simple working model and then proceed from there. 

#Day 3 - 12/03/2026
I like commenting to sort of track my working process. 
So now I will be reading about the Entsoe API. 
I guess my first goal is to get data about the wind forecast and the actual power generation
both onshore and offshore because for one wind is volatile and it produces the most electricity in Denmark. 
It has 2 clients, I will be using the EntsoePandasClient because I prefer my data as a Dataframe.
I found these 2 references to understand how to use the API and the parameters I would use:

1.https://github.com/EnergieID/entsoe-py?tab=readme-ov-file
2.[https://documenter.getpostman.com/view/7009892/2s93JtP3F6#e2e1a56e-2ee1-4b83-b1db-8a3d21cc0ac0](https://documenter.getpostman.com/view/7009892/2s93JtP3F6#e2e1a56e-2ee1-4b83-b1db-8a3d21cc0ac0) 
From the 2nd, I got the coutry codes and psr_types.
I printed the onshore and offshore shape to see how many rows of forecasted data I got.
The numbers seems a little odd. I guess I will ask claude if this number is expected for the period I am working with.
Claude says that the rows should be around 68000. I am not sure how to fix it, I will come back to it.

#Day 4 - 13/03/2026
Does ENTSOE not publish by the hour, the data I need? I guess I have to check.
I printed the head(20) and tail(20) of my wind forecast data and in 2018, they are hourly but in 2025 they are every 15 minutes, for some reason. Either I could take the specific hour time or maybe because of the volatility I should take the mean? I am not sure. Because also my data are in MW not MWh meaning, a measure of power at a specific time point. I will do the mean(), let's see. 




