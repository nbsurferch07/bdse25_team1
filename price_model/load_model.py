import numpy as np
import pandas as pd
import os
import pickle
from pathlib import Path

directory = Path(__file__).resolve().parent


def price_predict(city, region, bedroom, liv, bath, house_age, gar, floor, floor_all, area, house_type, house, material, org):
    if city == '台北市':
        with open(directory/"model_XGBR_taipei_ord.pickle", 'rb') as f:
            xbgr_load = pickle.load(f)
            dict_region = {'中山區': 0,
                           '中正區': 1,
                           '信義區': 2,
                           '內湖區': 3,
                           '北投區': 4,
                           '南港區': 5,
                           '士林區': 6,
                           '大同區': 7,
                           '大安區': 8,
                           '文山區': 9,
                           '松山區': 10,
                           '萬華區': 11}
    elif city == '新北市':
        with open(directory/"model_XGBR_newtaipei_ord.pickle", 'rb') as f:
            xbgr_load = pickle.load(f)
            dict_region = {'三峽區': 0,
                           '三芝區': 1,
                           '三重區': 2,
                           '中和區': 3,
                           '五股區': 4,
                           '八里區': 5,
                           '土城區': 6,
                           '坪林區': 7,
                           '平溪區': 8,
                           '新店區': 9,
                           '新莊區': 10,
                           '板橋區': 11,
                           '林口區': 12,
                           '樹林區': 13,
                           '永和區': 14,
                           '汐止區': 15,
                           '泰山區': 16,
                           '淡水區': 17,
                           '深坑區': 18,
                           '烏來區': 19,
                           '瑞芳區': 20,
                           '石碇區': 21,
                           '石門區': 22,
                           '萬里區': 23,
                           '蘆洲區': 24,
                           '貢寮區': 25,
                           '金山區': 26,
                           '雙溪區': 27,
                           '鶯歌區': 28}
    elif city == '桃園市':
        with open(directory/"model_XGBR_taoyuan_ord.pickle", 'rb') as f:
            xbgr_load = pickle.load(f)
            dict_region = {'中壢區': 0,
                           '八德區': 1,
                           '大園區': 2,
                           '大溪區': 3,
                           '平鎮區': 4,
                           '復興區': 5,
                           '新屋區': 6,
                           '桃園區': 7,
                           '楊梅區': 8,
                           '蘆竹區': 9,
                           '觀音區': 10,
                           '龍潭區': 11,
                           '龜山區': 12}
    elif city == '台中市':
        with open(directory/"model_XGBR_taichung_ord.pickle", 'rb') as f:
            xbgr_load = pickle.load(f)
            dict_region = {'中區': 0,
                           '北區': 1,
                           '北屯區': 2,
                           '南區': 3,
                           '南屯區': 4,
                           '后里區': 5,
                           '外埔區': 6,
                           '大安區': 7,
                           '大甲區': 8,
                           '大肚區': 9,
                           '大里區': 10,
                           '大雅區': 11,
                           '太平區': 12,
                           '新社區': 13,
                           '東勢區': 14,
                           '東區': 15,
                           '梧棲區': 16,
                           '沙鹿區': 17,
                           '清水區': 18,
                           '潭子區': 19,
                           '烏日區': 20,
                           '石岡區': 21,
                           '神岡區': 22,
                           '西區': 23,
                           '西屯區': 24,
                           '豐原區': 25,
                           '霧峰區': 26,
                           '龍井區': 27}
    elif city == '台南市':
        with open(directory/"model_XGBR_tainan_ord.pickle", 'rb') as f:
            xbgr_load = pickle.load(f)
            dict_region = {'七股區': 0,
                           '下營區': 1,
                           '中西區': 2,
                           '仁德區': 3,
                           '佳里區': 4,
                           '六甲區': 5,
                           '北區': 6,
                           '北門區': 7,
                           '南區': 8,
                           '善化區': 9,
                           '大內區': 10,
                           '學甲區': 11,
                           '安南區': 12,
                           '安定區': 13,
                           '安平區': 14,
                           '官田區': 15,
                           '將軍區': 16,
                           '山上區': 17,
                           '左鎮區': 18,
                           '後壁區': 19,
                           '新化區': 20,
                           '新市區': 21,
                           '新營區': 22,
                           '東區': 23,
                           '東山區': 24,
                           '柳營區': 25,
                           '楠西區': 26,
                           '歸仁區': 27,
                           '永康區': 28,
                           '玉井區': 29,
                           '白河區': 30,
                           '西港區': 31,
                           '關廟區': 32,
                           '鹽水區': 33,
                           '麻豆區': 34}
    elif city == '高雄市':
        with open(directory/"model_XGBR_kaohsiung_ord.pickle", 'rb') as f:
            xbgr_load = pickle.load(f)
            dict_region = {'三民區': 0,
                           '仁武區': 1,
                           '六龜區': 2,
                           '前金區': 3,
                           '前鎮區': 4,
                           '大寮區': 5,
                           '大樹區': 6,
                           '大社區': 7,
                           '小港區': 8,
                           '岡山區': 9,
                           '左營區': 10,
                           '彌陀區': 11,
                           '新興區': 12,
                           '旗山區': 13,
                           '旗津區': 14,
                           '林園區': 15,
                           '梓官區': 16,
                           '楠梓區': 17,
                           '橋頭區': 18,
                           '永安區': 19,
                           '湖內區': 20,
                           '燕巢區': 21,
                           '甲仙區': 22,
                           '美濃區': 23,
                           '苓雅區': 24,
                           '茄萣區': 25,
                           '路竹區': 26,
                           '阿蓮區': 27,
                           '鳥松區': 28,
                           '鳳山區': 29,
                           '鹽埕區': 30,
                           '鼓山區': 31}
                           
    rooms = int(bedroom)+int(liv)+int(bath)
    floor_ratio = int(floor)/int(floor_all)

    if material == '鋼骨鋼筋混凝土造':
        material = 1
    elif material == '鋼骨混凝土造':
        material = 2
    elif material == '鋼骨造':
        material = 3
    elif material == '鋼筋混凝土造':
        material = 4
    elif material == '加強磚造':
        material = 5

    if org == '有':
        org = 1
    else:
        org = 0

    dict_housetype = {'建物': 0, '房地(土地+建物)': 1, '房地(土地+建物)+車位': 2}
    dict_house = {'住宅大樓(11層含以上有電梯)': 0,
                  '公寓(5樓含以下無電梯)': 1,
                  '套房(1房1廳1衛)': 2,
                  '華廈(10層含以下有電梯)': 3,
                  '透天厝': 4}

    input_data = np.array([[dict_region[region], dict_housetype[house_type], 0, 9, int(
        floor_all), dict_house[house], material, org, rooms, int(area), int(house_age), 1, 1, int(gar),  floor_ratio]])
    columns = ['鄉鎮市區', '交易標的', '都市土地使用分區', '交易年', '總樓層數', '建物型態', '主要建材', '有無管理組織',
               '房間數', '建物移轉總面積坪', '屋齡', '土地', '建物', '車位', '樓層比']
    df = pd.DataFrame(input_data, columns=columns)
    #origin = origin[columns]
    # print(df)
    #df_concat = pd.concat([origin, df])
    #df_concat = df_concat.reset_index(drop=True)
    # print(df_concat['鄉鎮市區'].unique())
    #df_concat[['交易年', '總樓層數', '有無管理組織', '車位總價元', '屋齡', '房間數', '主要建材']] = df_concat[['交易年', '總樓層數', '有無管理組織', '車位總價元', '屋齡', '房間數', '主要建材']].astype('str').astype('float64').astype('int64')
    #df_concat[['建物移轉總面積坪', '樓層比']] = df_concat[['建物移轉總面積坪', '樓層比']].astype('str').astype('float64')
    #data = pd.get_dummies(df_concat).tail(1)
    # return print(data.columns)
    return xbgr_load.predict(df)


# price_predict('高雄市', '鼓山區', 1, 1, 1, 100000, 30, 5, 10, 40, '房地(土地+建物)+車位', '華廈(10層含以下有電梯)', "鋼筋混凝土造", "有")
