#%%
# Package we use for data processing
import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
pd.options.display.max_rows = 8
from download import download

# Package for the linear regression
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm
import statsmodels.formula.api as smf

#%%
# Download the data
url ="https://docs.google.com/spreadsheets/d/e/2PACX-1vQVtdpXMHB4g9h75a0jw8CsrqSuQmP5eMIB2adpKR5hkRggwMwzFy5kB-AIThodhVHNLxlZYm8fuoWj/pub?gid=2105854808&single=true&output=csv"
path_target = "Prediction.csv"
download(url, path_target, replace = True)

# First, I introduce some functions which will help me further
#%%
# Fonction : Rename the rows, they are numbered from 0 to the length of the dataframe
def rows(df):
    for i in range(len(df)):
        df.rename(index = {df.index[i]:i}, inplace=True)
    return(df)

#%%
# Fonction : Drop the weekends 
def drop_week(df):
    index_name = df[df['Day'] == 'Saturday'].index
    index_name2 = df[df['Day'] == 'Sunday'].index
    df = df.drop(index_name)
    df = df.drop(index_name2)
    return(rows(df))

#%%
# Function : Recalculate the total number of bikes
def bike_total(df):
    for i in range(len(df)):
        if i==0 :
            df.loc[i, 'Total bike'] = df.loc[i, 'Day bike']
        else :
            df.loc[i, 'Total bike'] = df.loc[i-1, 'Total bike'] + df.loc[i, 'Day bike']
    return(df)

#%%
####### Data selection  #######

# We load the data and we do a first sorting : remove useless columns and rows with NA
bike_raw = pd.read_csv(url)

# Renaming columns 
bike_raw.columns=['Date', 'Hour', 'Total bike','Day bike', 'Remarque', 'Unnamed: 4']
bike = bike_raw.copy()

# Remove rows with an empty value (NA)
bike = bike.drop(columns = ["Remarque", "Unnamed: 4"])
bike = bike.dropna(axis = 0, how='all')

# Change the format of the date
bike['Date'] = pd.to_datetime(bike['Date'], format="%d/%m/%Y") 

rows(bike)
bike

# %%
## Add the days of the week 

# Create the day for every unique date
df = bike.copy()
df = df.drop_duplicates(subset=['Date'])
rows(df)
ligne = np.arange(0,len(df))
df2 = pd.DataFrame(0, index = ligne, columns = ["Day"])
for i in range(len(df)):
    df2.loc[df2.index[i], 'Day'] = (i+3)%7 # because the data start on 12/03/2020 and it's a Thursday (3)
df_jour = pd.concat([df2,df], axis=1)

# Add a column "Day" in the initial dataframe
row = np.arange(0, len(bike))
jour = pd.DataFrame(0, index = row, columns = ["Day"])
bicycle_jour = pd.concat([jour,bike], axis=1)

#%%
# Now that we have a dataframe with an unique date in every rows and with an associated number, 
# we compare dates with the inital dataframe and we add the associated number 
for j in range(len(df_jour)):
    for i in range(len(bicycle_jour)):
        if bicycle_jour.loc[i, 'Date'] == df_jour.loc[j, 'Date']:
            bicycle_jour.loc[i, 'Day'] = df_jour.loc[j, 'Day']

#%%
# Change the numbers into days

bicycle_jour['Day'] = bicycle_jour['Day'].replace([0], 'Monday')
bicycle_jour['Day'] = bicycle_jour['Day'].replace([1], 'Tuesday')
bicycle_jour['Day'] = bicycle_jour['Day'].replace([2], 'Wednesday')
bicycle_jour['Day'] = bicycle_jour['Day'].replace([3], 'Thursday')
bicycle_jour['Day'] = bicycle_jour['Day'].replace([4], 'Friday')
bicycle_jour['Day'] = bicycle_jour['Day'].replace([5], 'Saturday')
bicycle_jour['Day'] = bicycle_jour['Day'].replace([6], 'Sunday')

# %%
# We only keep the hour between 08:20 and 09:30
bike2 = bicycle_jour.copy()
bike2 = bike2[(bike2["Hour"] <= "09:30") & (bike2["Hour"] >= "08:30")] 


# Si on a un jour en double, on garde seulement la derniere ligne dont la date est la meme
# If we have a day in double, we only keep the last row with the same date 
bike3 = bike2.copy()
bike3 = bike3.drop_duplicates(subset=['Date'], keep='last')
rows(bike3)

#%%
# New dataframe, we start at (the beginning of the year : 01/01/2021)
bike_part1 = bike3.copy()
bike_part2 = bike3.copy()
bike_part1 = bike_part1[(bike_part1['Date'] >= "2020-10-01") & (bike_part1['Date'] <="2020-10-31")]
bike_part2 = bike_part2[bike_part2['Date'] >= "2020-12-15"]
bike4 = pd.concat([bike_part1, bike_part2])
rows(bike4)
# bike4 = bike4[bike4['Date'] >= "2020-10-01"]
# rows(bike4)

# We drop now the week-end and we use the function bike_total
bike4 = drop_week(bike4)
bike_total(bike4)

# We drop days off (Christmas and New Year's Eve)
bike4 = bike4.drop(index = [6,7])
rows(bike4)
#%%
####### Prediction #######

## First approach :

# Mean/Median

# We are doing the mean and median of the entire dataset that we selected 
print(bike4.describe())
bike_med = bike4['Day bike'].median()
print(f'\nMedian = {bike_med}\n')

#%%
# And then/Just for the friday 
Friday = bike4[bike4['Day'] == 'Friday']
rows(Friday)
bike_total(Friday)

print(Friday.describe())
bike_med_fri = Friday['Day bike'].median()
print(f'\nMedian = {bike_med_fri}')

#%%%
## Second approach :

# Linear regression 

model = LinearRegression()
#  Creation of our X and y :
X = np.arange(0, len(bike4)).reshape((-1,1))
y = bike4['Total bike']

result = model.fit(X,y)
print(result.intercept_, result.coef_)

# Prediction : number of bikes estimated for tomorow :
bike_est = result.intercept_ + result.coef_*len(bike4) - bike4['Total bike'][len(bike4)-1]
print(f'Number of bikes estimated : {bike_est}')

#%%
# Friday only
model2 = LinearRegression()

# Creation of our X and y :
X2 = np.arange(0, len(Friday)).reshape((-1,1))
y2 = Friday['Total bike']

result2 = model.fit(X2,y2)
print(result2.intercept_, result2.coef_)

# Prediction : number of bikes estimated for tomorow :
bike_est_fri = result2.intercept_ + result2.coef_*len(Friday) - Friday['Total bike'][len(Friday)-1]
print(f'Number of bikes estimated : {bike_est_fri}')





#%%

X3 = np.arange(0, 23)
X3 = np.vander(X3, 2)

model3 = sm.OLS(y,X3)
result3 = model3.fit()

print(result3.summary())

#%%

model = LinearRegression()
#  Creation of our X and y :
X = np.arange(0, len(bike4)).reshape((-1,1))
y = bike4['Day bike']

result = model.fit(X,y)
print(result.intercept_, result.coef_)

# Prediction : number of bikes estimated for tomorow :
bike_est = result.intercept_ + result.coef_*len(bike4)
print(f'Number of bikes estimated : {bike_est}')


#%%
# Regression avec tous les jours de la semaine
results = smf.ols('Vélos_jour ~ Vélos_total', data = bicycle4).fit()
print(results.summary())
pred = results.predict(exog = dict)


# Regression avec seulement les Vendredi
results = smf.ols('Vélos_jour ~ Vélos_total', data = Friday).fit()
print(results.summary())

# %%
# Histogramme 
plt.hist(bicycle4["Vélos_jour"])
plt.show()

# Peut etre interessant
bicycle4.plot('Vélos_total', 'Jour')
plt.show()

