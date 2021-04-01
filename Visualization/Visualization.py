#%%
import numpy as numpy
import folium
import pandas as pd
import matplotlib.pyplot as plt
pd.options.display.max_rows = 8
import os
import imageio

# %%
# Create a map in the center of Montpellier. 
map = folium.Map(location=[43.616482, 3.874153], zoom_start=12)
#%%
# Before we start, i created some functions. 
# It's the same function used in the prediction part.
def rows(df):
    for i in range(len(df)):
        df.rename(index = {df.index[i]:i}, inplace=True)
    return(df)

# %%
# This function is used to remove some useless columns and to have the dataframe all start at 06/01/2021 (because df7 start at this date).
def drop(df):
    if df.size == 672:
        df = df
    else:
        df.drop(df.index[0:20], inplace = True)
    df.drop(columns = ['laneId','type','reversedLane'], inplace = True)
    rows(df)

#%%
# They are missing 4 dates from the df1 so we add it in the Compteur1.json file.
# To complete these date, I took the same day, one week before and after, and did the mean.
# 12/01/2021 Mardi (05 : 909/19 : 1142) : 1025
# {"intensity":1025,"laneId":121403593,"dateObserved":"2021-01-12T00:00:00/2021-01-13T00:00:00","location":{"coordinates":[3.896939992904663,43.60969924926758],"type":"Point"},"id":"MMM_EcoCompt_X2H19070220_202101100000","type":"TrafficFlowObserved","vehicleType":"bicycle","reversedLane":false}
# 13/01/2021 Mercredi (06 : 959/20 : 706) : 832
# {"intensity":832,"laneId":121403593,"dateObserved":"2021-01-13T00:00:00/2021-01-14T00:00:00","location":{"coordinates":[3.896939992904663,43.60969924926758],"type":"Point"},"id":"MMM_EcoCompt_X2H19070220_202101100000","type":"TrafficFlowObserved","vehicleType":"bicycle","reversedLane":false}
# 16/01/2021 Samedi (09 : 510/23 : 927) : 718
# {"intensity":718,"laneId":121403593,"dateObserved":"2021-01-16T00:00:00/2021-01-17T00:00:00","location":{"coordinates":[3.896939992904663,43.60969924926758],"type":"Point"},"id":"MMM_EcoCompt_X2H19070220_202101100000","type":"TrafficFlowObserved","vehicleType":"bicycle","reversedLane":false}
# 17/01/2021 Dimanche (10 : 552/24 : 971) : 761
# {"intensity":761,"laneId":121403593,"dateObserved":"2021-01-17T00:00:00/2021-01-18T00:00:00","location":{"coordinates":[3.896939992904663,43.60969924926758],"type":"Point"},"id":"MMM_EcoCompt_X2H19070220_202101100000","type":"TrafficFlowObserved","vehicleType":"bicycle","reversedLane":false}

#%%
# Creation of all the dataframe.
df1= pd.read_json('Compteur1.json')
drop(df1)
df1 = df1.drop_duplicates(subset=['dateObserved'], keep='last')
rows(df1)
df2= pd.read_json('Compteur2.json')
drop(df2)
df3= pd.read_json('Compteur3.json')
drop(df3)
df4= pd.read_json('Compteur4.json')
drop(df4)
df5= pd.read_json('Compteur5.json') 
drop(df5)
df6= pd.read_json('Compteur6.json')
drop(df6)
df7= pd.read_json('Compteur7.json')
drop(df7)
df8= pd.read_json('Compteur8.json')
drop(df8)

# %%
# I created two dictionary which will help us later. One with all the dataframe and the the other one just the localisation of every bike counter.
coordinates = {1:df1['location'][1], 2:df2['location'][1], 3:df3['location'][1], 4:df4['location'][1], 5:df5['location'][1], 6:df6['location'][1], 7:df7['location'][1], 8:df8['location'][1]}
bike = {1:df1, 2:df2, 3:df3, 4:df4, 5:df5, 6:df6, 7:df7, 8:df8}

#%%
# Exchange the position of the coordinates (otherwise we are not in France). 
point = []
for i in range(1,9):
    point = point + [list(coordinates[i].values())[0]]
    point[i-1][0], point[i-1][1] = point[i-1][1], point[i-1][0]

#%%
# Create all the maps since 06/01/2021 and save them in HTML format.
Mtp_map = {}
for i in range(0,84):
    Mtp_map[i] = folium.Map(location=[43.616482, 3.874153], zoom_start=12, tiles='CartoDB dark_matter')
    for j in range(1,9):
        folium.CircleMarker(radius = bike[j]['intensity'][i]/100, location = point[j-1], color = 'gold', fill = True).add_to(Mtp_map[i])
    Mtp_map[i].save(f'Day{i+1}.html')

#%%
# Creation of the gif thanks to png files. 
png_dir = 'C:/Users/sobol/HMMA238/Projects/Velo/Png file'
images = []
for file_name in sorted(os.listdir(png_dir)):
    if file_name.endswith('.png'):
        file_path = os.path.join(png_dir, file_name)
        images.append(imageio.imread(file_path))
imageio.mimsave('C:/Users/sobol/HMMA238/Projects/Velo/Gif/challenge.gif', images, fps = 2)
# %%
#%%
# import os
# import imageio

# path = 'C:/Users/sobol/HMMA238/Projects/Velo/Html file'

# image_folder = os.fsencode(path)

# filenames = []

# for file in os.listdir(image_folder):
#     filename = os.fsdecode(file)
#     if filename.endswith( ('.html') ):
#         filenames.append(filename)
# images = list(map(lambda filename: imageio.imread(filename), filenames))

# imageio.mimsave(os.path.join(path, '../Vizualisation/gif'), images, duration = 0.04)
# # %%