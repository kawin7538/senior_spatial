from bs4 import BeautifulSoup
import numpy as np
import requests
import re
import pandas as pd
from tqdm import tqdm

url='http://service.nso.go.th/nso/web/statseries/statseries27.html'

def get_html(url):
    response=requests.get(url)
    return response.text

def get_all_items(html):
    soup=BeautifulSoup(html,'lxml')
    links=[]
    for link in soup.findAll('a',attrs={'href':re.compile('rain-46-58.xls$')}):
        links.append(link.get('href'))
    return links

def export_df(list_links,keyword1,keyword2):
    total_rain_df=pd.DataFrame()

    for link in tqdm(list_links):
        # print(link.split('/')[1])
        df=pd.read_excel(f"http://service.nso.go.th/nso/web/statseries/{link}",skiprows=[0,1,2,3,5],skipfooter=4,header=0)
        df=df.dropna()
        new_col=list(range(2003,2016))
        df.columns=[list(df.columns)[0]]+new_col+[list(df.columns)[-1]]
        new_df=pd.DataFrame(columns=new_col)
        new_df=new_df.append(df.loc[df['Item']==keyword1].iloc[:,1:14])
        new_df=new_df.assign(Area=' '.join(link.split('/')[1].split('_')[1:])).reset_index(drop=True)
        total_rain_df=total_rain_df.append(new_df)

    total_rain_df=total_rain_df.replace('-',np.nan).replace('-   ',np.nan)
    # print(total_rain_df.fillna(0).info())
    total_rain_df.to_csv(f"preprocessed_data/{keyword2}.csv",index=False)
    total_rain_df.fillna(0).groupby('Area').agg('mean').reset_index().replace(0,np.nan).to_csv(f"preprocessed_data/mean_{keyword2}.csv",index=False)

if __name__=='__main__':
    html=get_html(url)
    list_links=get_all_items(html)

    export_df(list_links,"Total rain (millimeter)","total_rain")
    export_df(list_links,"Number of rainy days (day)","cnt_day_rain")

    mean_total_df=pd.read_csv("preprocessed_data/mean_total_rain.csv")
    mean_cnt_df=pd.read_csv("preprocessed_data/mean_cnt_day_rain.csv")

    mean_totalperday_df=mean_total_df.select_dtypes(exclude=['object'])/mean_cnt_df.select_dtypes(exclude=['object'])
    mean_totalperday_df['Area']=mean_total_df['Area']
    mean_totalperday_df.to_csv("preprocessed_data/mean_totalperday_rain.csv",index=False)