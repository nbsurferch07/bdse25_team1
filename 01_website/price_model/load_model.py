import numpy as np
import pandas as pd
import os
import pickle
from pathlib import Path

directory = Path(__file__).resolve().parent

def price_predict(city, region, bedroom, liv, bath, gar_price,house_age, floor, floor_all, area, house_type, house, material, org):
    if city == '台北市':
        with open(directory/"model_XGBR_taipei.pickle", 'rb') as f:
            xbgr_load = pickle.load(f)
        origin=pd.read_csv(directory/"taipei_unique.csv",engine='python',index_col=[0])
    elif city == '新北市':
        with open(directory/"model_XGBR_newtaipei.pickle", 'rb') as f:
            xbgr_load = pickle.load(f)
        origin=pd.read_csv(directory/"newtaipei_unique.csv",engine='python',index_col=[0])
    elif city == '桃園市':
        with open(directory/"model_XGBR_taoyuan.pickle", 'rb') as f:
            xbgr_load = pickle.load(f)
        origin=pd.read_csv(directory/"taoyuan_unique.csv",engine='python',index_col=[0])
    elif city == '台中市':
        with open(directory/"model_XGBR_taichung.pickle", 'rb') as f:
            xbgr_load = pickle.load(f)
        origin=pd.read_csv(directory/"taichung_unique.csv",engine='python',index_col=[0])
    elif city == '台南市':
        with open(directory/"model_XGBR_tainan.pickle", 'rb') as f:
            xbgr_load = pickle.load(f)
        origin=pd.read_csv(directory/"tainan_unique.csv",engine='python',index_col=[0])
    elif city == '高雄市':
        with open(directory/"model_XGBR_kaohsiung.pickle", 'rb') as f:
            xbgr_load = pickle.load(f)
        origin=pd.read_csv(directory/"kaohsiung_unique.csv",engine='python',index_col=[0])
    rooms=int(bedroom)+int(liv)+int(bath)
    floor_ratio=int(floor)/int(floor_all)

    if material=='鋼骨鋼筋混凝土造':
        material=1
    elif material=='鋼骨混凝土造':
        material=2
    elif material=='鋼骨造':
        material=3
    elif material=='鋼筋混凝土造':
        material=4
    elif material=='加強磚造':
        material=5

    if org=='有':
        org=1
    else:
        org=0

    input_data=np.array([[region, house_type, '住', 10, int(floor_all), house, material, org, int(gar_price), int(area), int(house_age), rooms, floor_ratio]])
    columns=['鄉鎮市區', '交易標的', '都市土地使用分區', '交易年', '總樓層數', '建物型態', '主要建材', '有無管理組織',
       '車位總價元', '建物移轉總面積坪', '屋齡', '房間數', '樓層比']
    df=pd.DataFrame(input_data,columns=columns)
    origin=origin[columns]
    # print(df)
    df_concat=pd.concat([origin,df])
    df_concat=df_concat.reset_index(drop=True)
    # print(df_concat['鄉鎮市區'].unique())
    df_concat[['交易年', '總樓層數','有無管理組織','車位總價元', '屋齡', '房間數','主要建材']]=df_concat[['交易年', '總樓層數','有無管理組織','車位總價元', '屋齡', '房間數','主要建材']].astype('str').astype('float64').astype('int64')
    df_concat[['建物移轉總面積坪', '樓層比']]=df_concat[['建物移轉總面積坪', '樓層比']].astype('str').astype('float64')
    data = pd.get_dummies(df_concat).tail(1)
    # return print(data.columns)
    return xbgr_load.predict(data)


# price_predict('高雄市', '鼓山區', 1, 1, 1, 100000, 30, 5, 10, 40, '房地(土地+建物)+車位', '華廈(10層含以下有電梯)', "鋼筋混凝土造", "有")