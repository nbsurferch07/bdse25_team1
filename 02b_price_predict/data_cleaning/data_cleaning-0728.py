#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import sys

# load data
def load_data(city,cityid):
    df_a = pd.read_csv('Desktop/house-price/house_price_predict/concat/all_'+cityid+'_'+city+'_A.csv', engine='python')
    df_b = pd.read_csv('Desktop/house-price/house_price_predict/concat/all_'+cityid+'_'+city+'_B.csv', engine='python')
    return df_a, df_b

def remove_na(df):
    # remove garage & land & NaN columns
    con1 = df["交易標的"] != "車位"
    con2 = df["交易標的"] != "土地"
    df = df[con1 & con2]
    df = df.dropna()
    return df

def land_area_select(df):
    # 篩選"土地使用分區"
    df.loc[df['都市土地使用分區'].str.contains('住'),'都市土地使用分區']='住'
    df.loc[df['都市土地使用分區'].str.contains('商'),'都市土地使用分區']='商'
    df=df[~df['都市土地使用分區'].str.contains('都市')]
    df=df[((df['都市土地使用分區']!='農') & (df['都市土地使用分區']!='工'))]
    # 篩選"建物型態"
    df=df[~df['建物型態'].isin(['店面(店鋪)','辦公商業大樓','其他','廠辦'])]
    # 主要用途篩選住家用
    df=df[df['主要用途']=='住家用']
    return df

def material_select(df):
    # 篩選"主要建材"
    df=df.groupby("主要建材").filter(lambda ing: len(ing) > 500)
    df=df[df['主要建材']!='見其他登記事項']
    df=df[df['主要建材']!='見使用執照']
    # 主要建材編碼
    df.loc[(df['主要建材'].isin(['鋼骨鋼筋混凝土造','鋼骨鋼筋混凝土構造'])),['主要建材']]=1
    df.loc[df['主要建材'].isin(['鋼骨混凝土造']),['主要建材']]=2
    df.loc[(df['主要建材'].isin(['鋼骨造','鋼骨構造'])),['主要建材']]=3
    df.loc[(df['主要建材'].isin(['鋼筋混凝土造','鋼筋混凝土構造','鋼造','鋼筋混凝土加強磚造','鋼筋混凝土'])),['主要建材']]=4
    df.loc[(df['主要建材'].isin(['加強磚造','磚造'])),['主要建材']]=5
    df['主要建材']=df['主要建材'].astype('int64')
    return df

def floor_select(df):
    
    # 將移轉層次"全"改為總樓層數
    df.loc[df[df['移轉層次']=='全'].index,'移轉層次']=df.loc[df[df['移轉層次']=='全'].index,'總樓層數']
    
    # delete useless floor
    useless_floor = df["移轉層次"].str.len() > 6
    df = df[~useless_floor]

    # modify floor value
    df.loc[:,"移轉層次"] = df.loc[:,"移轉層次"].str[:2]

    # select count value > 500
    df = df.groupby("移轉層次").filter(lambda grp: len(grp) > 500)

    # 刪除"移轉層次"與"總樓層數"不合理欄位
    df=df[~df['移轉層次'].isin(['陽台','地下','(空白)','見其他登記事項','見使用執照','社登'])]
    df=df[~df['總樓層數'].isin(['陽台','地下','(空白)','見其他登記事項','見使用執照','社登'])]
    df=df[(df["總樓層數"]!='0') & (df["總樓層數"]!=0)]
    return df

def room_handling(df):
    # 刪除只有"衛"的欄位
    df_mask1=df["建物現況格局-房"]==0
    df_mask2=df["建物現況格局-廳"]==0
    df_mask3=df["建物現況格局-衛"]==1
    df=df[~(df_mask1 & df_mask2 & df_mask3)]

    # 將房廳衛000設為111
    df_mask4=df["建物現況格局-房"]==0
    df_mask5=df["建物現況格局-廳"]==0
    df_mask6=df["建物現況格局-衛"]==0
    df.loc[df_mask4 & df_mask5 & df_mask6, ["建物現況格局-房","建物現況格局-廳","建物現況格局-衛"]]=1

    # 新增房間數 (因房廳衛相關性高故房+廳+衛=房間數)
    df["房間數"]=df["建物現況格局-房"]+df["建物現況格局-廳"]+df["建物現況格局-衛"]
    df=df.drop(["建物現況格局-房","建物現況格局-廳","建物現況格局-衛"],axis=1)
    df=df[df['房間數']<10]
    return df

def ordinal_encoding(df):
     # 總樓層數編碼
    new_all_floor = {"總樓層數": 
                 {"一層" : 1, 
                  "二層" : 2, 
                  "三層" : 3, 
                  "四層" : 4, 
                  "五層" : 5, 
                  "六層" : 6, 
                  "七層" : 7, 
                  "八層" : 8, 
                  "九層" : 9, 
                  "十層" : 10, 
                  "十一層" : 11, 
                  "十二層" : 12, 
                  "十三層" : 13, 
                  "十四層" : 14, 
                  "十五層" : 15, 
                  "十六層" : 16, 
                  "十七層" : 17, 
                  "十八層" : 18, 
                  "十九層" : 19, 
                  "二十層" : 20,
                  "二十一層" : 21, 
                  "二十二層" : 22, 
                  "二十三層" : 23, 
                  "二十四層" : 24, 
                  "二十五層" : 25, 
                  "二十六層" : 26, 
                  "二十七層" : 27, 
                  "二十八層" : 28, 
                  "二十九層" : 29, 
                  "三十層" : 30,
                  "三十一層" : 31,
                  "三十二層" : 32,
                  "三十三層" : 33,
                  "三十四層" : 34,
                  "三十五層" : 35,
                  "三十六層" : 36,
                  "三十七層" : 37,
                  "三十八層" : 38,
                  "三十九層" : 39,
                  "四十層" : 40,
                  "四十一層" : 41,
                  "四十二層" : 42,
                  "四十三層" : 43,
                  "四十六層" : 46,
                  "六十八層" : 68
                 }
                }
    # 移轉層次編碼
    new_floor = {"移轉層次": 
                 {"一層" : 1, 
                  "二層" : 2, 
                  "三層" : 3, 
                  "四層" : 4, 
                  "五層" : 5, 
                  "六層" : 6, 
                  "七層" : 7, 
                  "八層" : 8, 
                  "九層" : 9, 
                  "十層" : 10, 
                  "十一" : 11, 
                  "十二" : 12, 
                  "十三" : 13, 
                  "十四" : 14, 
                  "十五" : 15, 
                  "十六" : 16, 
                  "十七" : 17, 
                  "十八" : 18, 
                  "十九" : 19, 
                  "二十" : 20,
                  "三十" : 30
                 }
                }
    df = df.replace(new_all_floor)
    df["總樓層數"]=df["總樓層數"].astype('int64')
    df = df.replace(new_floor)
    df["移轉層次"]=df["移轉層次"].astype('int64')
    
    # 有無管理組織編碼
    df.loc[df['有無管理組織']=='有',['有無管理組織']]=1
    df.loc[df['有無管理組織']=='無',['有無管理組織']]=0
    df['有無管理組織']=df['有無管理組織'].astype('int64')
    return df
    
def price_calculation(df):
    # 計算每坪價格
    df['總價元']=df['總價元']/10000
    df['建物移轉總面積坪']=df['建物移轉總面積平方公尺']*0.3025
    df['每坪價格']=(df['總價元'])/df['建物移轉總面積坪']
    df=df[df['建物移轉總面積平方公尺']!=0]
    
    # 計算屋齡
    df['建築完成年'] = df['建築完成年月'].astype('float64')//10000
    df['屋齡']=(df['交易年']-df['建築完成年']).astype('int64')
    mask_year=df['屋齡']>-10
    df=df[mask_year]
    
    # 產生車位
    a=df["交易筆棟數"].str.split("土地|建物|車位", expand=True)
    df["車位"]=a[3].astype('int64')
    
    # 刪除車位=0 車位總價元=\=0
    mask_garzero=(df['車位總價元']!=0) & (df['車位']==0)
    df=df[~mask_garzero]
    df['車位總價元']=df['車位總價元']/10000
    
    # 篩選不合理資料
    df=df[(df['建物移轉總面積坪']<=1000) & (df['建物移轉總面積坪']>5)]
    df=df[(df['每坪價格']<=800) & (df['每坪價格']>10)]
    df=df[df['車位']<10]
    return df

def price_normalization(df):
    # normalization 每坪價格
    max_std=df['每坪價格'].mean()+3*df['每坪價格'].std()

    # 移除 outliner
    mask_3=df['每坪價格']>max_std
    df=df[~mask_3]

    # normalization 建物移轉總面積坪
    max_std=df['建物移轉總面積坪'].mean()+3*df['建物移轉總面積坪'].std()

    # 移除 outliner
    mask_5=df['建物移轉總面積坪']>max_std
    df=df[~mask_5]
    return df

def column_select(df):
    df = df[["鄉鎮市區","交易標的", "建物移轉總面積平方公尺","都市土地使用分區","交易年","交易筆棟數","移轉層次","總樓層數","建物型態","主要用途","主要建材","建築完成年月","建物現況格局-房","建物現況格局-廳","建物現況格局-衛","有無管理組織","總價元","單價元平方公尺" ,"車位總價元"]]
    return df
def data_clean(df_a,df_b):
    # df_b預售屋無建築完成年月 
    df_b['建築完成年月']=df_b['交易年月日']
    
    # concat two dataframe
    df = pd.concat([df_a, df_b],ignore_index=True)

    # slice datetime
    df['交易年'] = (df['交易年月日']/10000).astype('int64')
    
    df=column_select(df)

    df=remove_na(df)
    
    # 移除符號
    column=df['建築完成年月'].astype('str')
    mask_dash=column.str.contains(' ') | column.str.contains('-') | column.str.contains('/')
    df=df[~mask_dash]
    
    df=land_area_select(df)
    df=material_select(df)
    df=room_handling(df)
    df=floor_select(df)
    df=price_calculation(df)
    df=price_normalization(df)
    df=ordinal_encoding(df)
    
    # 移除樓層數大於8的透天厝
    df=df[~((df['建物型態']=='透天厝') & (df['總樓層數']>8))]
    # 新增樓層比欄位
    df['樓層比']=df['移轉層次']/df['總樓層數']
    
    # 刪除不用的欄位
    df=df.drop(['主要用途','移轉層次','交易筆棟數','建物移轉總面積平方公尺','單價元平方公尺','建築完成年月','建築完成年','總價元'],axis=1)

    # 取用2013年以後的資料
    df=df[df['交易年']>=102]
    
    # 交易年編碼
    new_year = {"交易年": 
                 {102 : 1, 
                  103 : 2, 
                  104 : 3, 
                  105 : 4, 
                  106 : 5, 
                  107 : 6, 
                  108 : 7, 
                  109 : 8, 
                  110 : 9, 
                  111 : 10
                 }
                }
    df = df.replace(new_year)
    return df

def ohe(df):
    # onehot encoding
    df_oh=pd.get_dummies(df)
    df_oh.to_csv('Desktop/house-price/house_price_predict/'+city+'_predictset_onehot_test.csv')
    print('done')
    return 


city=input('請輸入城市：')
cityid=input('請輸入城市id：')
df_a, df_b=load_data(city,cityid)
df=data_clean(df_a, df_b)
ohe(df)