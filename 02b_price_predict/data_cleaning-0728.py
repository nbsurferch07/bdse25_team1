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

def data_clean(df_a,df_b):
    
    # df_b預售屋無建築完成年月 
    df_b['建築完成年月']=df_b['交易年月日']
    
    # concat two dataframe
    df = pd.concat([df_a, df_b],ignore_index=True)

    # slice datetime
    df['交易年'] = (df['交易年月日']/10000).astype('int64')
    
    # select specific columns with fancy index
    df_fi = df[["鄉鎮市區","交易標的", "建物移轉總面積平方公尺","都市土地使用分區","交易年","交易筆棟數","移轉層次","總樓層數","建物型態","主要用途","主要建材","建築完成年月","建物現況格局-房","建物現況格局-廳","建物現況格局-衛","有無管理組織","總價元","單價元平方公尺" ,"車位總價元"]]
    
    # remove garage & land & NaN columns
    con1 = df_fi["交易標的"] != "車位"
    con2 = df_fi["交易標的"] != "土地"
    df_no_gar_land = df_fi[con1 & con2]
    df_dropna = df_no_gar_land.dropna()

    # 篩選"建物型態"
    df_type=df_dropna.copy()
    df_type=df_type[~df_type['建物型態'].isin(['店面(店鋪)','辦公商業大樓','其他','廠辦'])]

    # 篩選"土地使用分區"
    df_type.loc[df_type['都市土地使用分區'].str.contains('住'),'都市土地使用分區']='住'
    df_type.loc[df_type['都市土地使用分區'].str.contains('商'),'都市土地使用分區']='商'
    df_landuse=df_type[~df_type['都市土地使用分區'].str.contains('都市')]
    df_landuse=df_landuse[((df_landuse['都市土地使用分區']!='農') & (df_landuse['都市土地使用分區']!='工'))]

    # 篩選"主要建材"
    df_ing=df_landuse.groupby("主要建材").filter(lambda ing: len(ing) > 500)
    df_ing=df_ing[df_ing['主要建材']!='見其他登記事項']

    # delete useless floor
    useless_floor = df_ing["移轉層次"].str.len() > 6
    df_floorclr = df_ing[~useless_floor]

    # modify floor value
    df_floormod=df_floorclr.copy()
    df_floormod["移轉層次"] = df_floormod["移轉層次"].str[:2]

    # select count value > 500
    df_floormod = df_floormod.groupby("移轉層次").filter(lambda grp: len(grp) > 500)

    # 刪除"移轉層次"與"總樓層數"不合理欄位
    df_floor_all=df_floormod[~df_floormod['移轉層次'].isin(['陽台','地下','(空白)','見其他登記事項','見使用執照','社登'])]

    # 刪除只有"衛"的欄位
    df_mask1=df_floor_all["建物現況格局-房"]==0
    df_mask2=df_floor_all["建物現況格局-廳"]==0
    df_mask3=df_floor_all["建物現況格局-衛"]==1
    df_pattern_del_001=df_floor_all[~(df_mask1 & df_mask2 & df_mask3)]

    # 將房廳衛000設為111
    df_mask4=df_pattern_del_001["建物現況格局-房"]==0
    df_mask5=df_pattern_del_001["建物現況格局-廳"]==0
    df_mask6=df_pattern_del_001["建物現況格局-衛"]==0
    df_pattern_del_001.loc[df_mask4 & df_mask5 & df_mask6, ["建物現況格局-房","建物現況格局-廳","建物現況格局-衛"]]=1
    df_pattern_del_111=df_pattern_del_001
    df_pattern_del_111=df_pattern_del_111[df_pattern_del_111['建物移轉總面積平方公尺']!=0]

    # 計算每坪價格
    df_cal=df_pattern_del_111.copy()
    df_cal['總價元']=df_cal['總價元']/10000
    df_cal['建物移轉總面積坪']=df_cal['建物移轉總面積平方公尺']*0.3025
    df_cal['每坪價格']=(df_cal['總價元'])/df_cal['建物移轉總面積坪']

    # separate 交易筆棟數
    df_sep=df_cal.copy()
    a=df_cal["交易筆棟數"].str.split("土地|建物|車位", expand=True)
    df_sep["車位"]=a[3].astype('int64')

    # 移除符號
    column=df_sep['建築完成年月'].astype('str')
    mask_dash=column.str.contains(' ') | column.str.contains('-') | column.str.contains('/')
    df_del_dash=df_sep[~mask_dash]

    # 計算屋齡
    df_del_dash['建築完成年'] = df_del_dash['建築完成年月'].astype('float64')//10000
    df_del_dash['屋齡']=(df_del_dash['交易年']-df_del_dash['建築完成年']).astype('int64')
    mask_year=df_del_dash['屋齡']>-10
    df_del_year=df_del_dash[mask_year]

    # 新增房間數 (因房廳衛相關性高故房+廳+衛=房間數)
    df_main_room=df_del_year.copy()
    df_main_room["房間數"]=df_main_room["建物現況格局-房"]+df_main_room["建物現況格局-廳"]+df_main_room["建物現況格局-衛"]
    df_main_room=df_main_room.drop(["建物現況格局-房","建物現況格局-廳","建物現況格局-衛"],axis=1)

    # 篩選"主要用途"含"住"
    df_main_living=df_main_room.loc[df_main_room["主要用途"].str.contains('住')]

    # 篩選"主要用途"移除有複雜說明欄位
    df_main_usage=df_main_living[df_main_living['主要用途'].isin(['住家用','國民住宅','集合住宅','住商用'])]

    # 刪除車位=0 車位總價元=\=0
    mask_garzero=(df_main_usage['車位總價元']!=0) & (df_main_usage['車位']==0)
    df_main_usage=df_main_usage[~mask_garzero]

    # 篩選不合理坪數及價格
    df_main_usage=df_main_usage[(df_main_usage['建物移轉總面積坪']<=1000) & (df_main_usage['建物移轉總面積坪']>5)]
    df_main_usage=df_main_usage[(df_main_usage['每坪價格']<=800) & (df_main_usage['每坪價格']>10)]

    # normalization 每坪價格
    max_std=df_main_usage['每坪價格'].mean()+3*df_main_usage['每坪價格'].std()

    # 移除 outliner
    mask_3=df_main_usage['每坪價格']>max_std
    df_outlier_std=df_main_usage[~mask_3]

    # normalization 建物移轉總面積坪
    max_std=df_outlier_std['建物移轉總面積坪'].mean()+3*df_outlier_std['建物移轉總面積坪'].std()

    # 移除 outliner
    mask_5=df_outlier_std['建物移轉總面積坪']>max_std
    df_outlier_all_std=df_outlier_std[~mask_5]
    df_outlier_all_std=df_outlier_all_std.reset_index(drop=True)

    # 將移轉層次"全"改為總樓層數
    df_all=df_outlier_all_std.copy()
    df_all.loc[df_all[df_all['移轉層次']=='全'].index,'移轉層次']=df_all.loc[df_all[df_all['移轉層次']=='全'].index,'總樓層數']

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
    df_floor_all = df_all.replace(new_all_floor)
    df_floor_all=df_floor_all[df_floor_all["總樓層數"]!='(空白)']
    df_floor_all=df_floor_all[df_floor_all["總樓層數"]!='見其他登記事項']
    df_floor_all=df_floor_all[df_floor_all["總樓層數"]!='見使用執照']
    df_floor_all=df_floor_all[df_floor_all["總樓層數"]!='社登']
    df_floor_all["總樓層數"]=df_floor_all["總樓層數"].astype('int64')
    
    # 移除樓層數大於8的透天厝
    df_floor_all=df_floor_all[~((df_floor_all['建物型態']=='透天厝') & (df_floor_all['總樓層數']>8))]

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
    df_floornum = df_floor_all.replace(new_floor)
    df_floornum["移轉層次"]=df_floornum["移轉層次"].astype('int64')
    
    # 新增樓層比欄位
    df_floornum['樓層比']=df_floornum['移轉層次']/df_floornum['總樓層數']

    # 主要建材編碼
    df_floornum.loc[(df_floornum['主要建材']=='鋼骨鋼筋混凝土造') | (df_floornum['主要建材']=='鋼骨鋼筋混凝土構造'),['主要建材']]=1
    df_floornum.loc[df_floornum['主要建材']=='鋼骨混凝土造',['主要建材']]=2
    df_floornum.loc[(df_floornum['主要建材']=='鋼骨造')| (df_floornum['主要建材']=='鋼骨構造'),['主要建材']]=3
    df_floornum.loc[(df_floornum['主要建材']=='鋼筋混凝土造') | (df_floornum['主要建材']=='鋼筋混凝土構造')| (df_floornum['主要建材']=='鋼造')| (df_floornum['主要建材']=='鋼筋混凝土加強磚造')| (df_floornum['主要建材']=='鋼筋混凝土'),['主要建材']]=4
    df_floornum.loc[(df_floornum['主要建材']=='加強磚造') | (df_floornum['主要建材']=='磚造'),['主要建材']]=5
    df_floornum=df_floornum[df_floornum['主要建材']!='見使用執照']
    df_floornum=df_floornum[df_floornum['主要建材']!='見其它登記事項']
    df_floornum['主要建材']=df_floornum['主要建材'].astype('int64')

    # 有無管理組織編碼
    df_floornum.loc[df_floornum['有無管理組織']=='有',['有無管理組織']]=1
    df_floornum.loc[df_floornum['有無管理組織']=='無',['有無管理組織']]=0
    df_floornum['有無管理組織']=df_floornum['有無管理組織'].astype('int64')

    # 主要用途篩選住家用
    df_usage=df_floornum[df_floornum['主要用途']=='住家用']

    # 刪除不用的欄位
    df_usage=df_usage.drop(['主要用途','移轉層次','交易筆棟數','建物移轉總面積平方公尺', '單價元平方公尺','車位總價元','建築完成年月','建築完成年','總價元'],axis=1)

    # 移除車位數房間數大於10的資料
    df_usage=df_usage[df_usage['車位']<10]
    df_usage=df_usage[df_usage['房間數']<10]

    # 取用2013年以後的資料
    df_usage=df_usage[df_usage['交易年']>=102]

    # 交易年編碼
    df_usage['交易年'].value_counts()
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
    df_new_year = df_usage.replace(new_year)
    return df_new_year

def ohe(df):
    # onehot encoding
    df_oh=pd.get_dummies(df)
    df_oh.to_csv('Desktop/house-price/house_price_predict/'+city+'_predictset_onehot.csv')
    return 'done'


city=input('請輸入城市：')
cityid=input('請輸入城市id：')
df_a, df_b=load_data(city,cityid)
df=data_clean(df_a, df_b)
ohe(df)