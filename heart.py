import os
import pandas as pd
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

df = pd.read_csv('heartoftuxes.csv', header=0)
#with pd.option_context('display.max_rows', None, 'display.max_columns', 10):
#    print(df.head(3))


df_meditation = df.loc[df["subreddit"] == "Meditation"]
df_buddhism = df.loc[df["subreddit"] == "Buddhism"]
df_malefashion = df.loc[df["subreddit"] == "malefashionadvice"]

print (df_meditation.iloc[1]['body'])



#print(df_meditation.loc[1, 1])
#with pd.option_context('display.max_rows', None, 'display.max_columns', 3):
#    print(df_meditation['body'][1])
