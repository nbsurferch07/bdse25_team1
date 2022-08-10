# BDSE25 Team1 project 家圖四必

### Outline

- [About](#about)
- [Demo](#demo)
- [Usage](#usage)
- [Contents](#contents)
- [Web Architecture](#web-architecture)
- [Quick start](#quick-start)
- [Acknowledgments](#acknowledgments)



## About
 
台灣房價逐年攀升，買第一間房的平均年齡上升至35-40歲，還完30年房貸年齡已近70，換房的可能性相對降低許多；在房價維持在如此高檔的情況下，發現風水上的瑕疵很難有能力換屋，但在台灣有60%的人買房重視風水。因此，若能透過歷年房價分析房價趨勢搭配格局圖的風水檢測，更能讓一般市井小名買得安心、住的放心。

<p align="right">(<a href="#top">back to top</a>)</p>



## Demo

[苡晏影片]  
![Demo video](01_website/static/img/testimonial-2.jpg)


<p align="right">(<a href="#top">back to top</a>)</p>



## Usage

* 檢視台灣歷年房價
* 預測台灣直轄市房屋價格
* 提供貸款能力試算
* 檢測格局圖風水


<p align="right">(<a href="#top">back to top</a>)</p>



## Contents

* 房價預測 (based on Hadoop cluster)
    * 資料清洗
    * 特徵工程
    * 模型訓練
    
* 歷年房價資訊
    * 資料處理與視覺化

* 格局圖影像辨識
    * 房間邊緣辨識
    * OCR偵測
    * 風水判斷
    
* 房貸與可負擔房價計算


<p align="right">(<a href="#top">back to top</a>)</p>




## Web Architecture
```
bdse25_team1 project
|__ main.py: set all route
|__ app.py: establish conntection with database
|__ model.py: create all Tables
|__ form_register.py: set account information form
|__ requirements.txt: all python package requirements
|__ static
|   |__ css
|   |   |__ css files
|   |       ...
|   |       ...
|   |__ img
|   |   |__ image files
|   |       ...
|   |       ...
|   |__ js
|   |   |__ javascripts files
|   |       ...
|   |       ...
|   |__ lib
|   |   |__ template for css files
|   |       ...
|   |       ...
|   |__ pattern_img
|       |__ result images after Fengshui recognition
|           ...
|           ...
|
|__ templates
|   |__ all html files
|       ...
|       ...
|
|__ price_model
|   |__ model_XGBR_taipei.pickle: model for taipei city
|   |__ model_XGBR_newtaipei.pickle: model for new taipei city
|   |__ model_XGBR_taoyuan.pickle: model for taoyuan city
|   |__ model_XGBR_taichung.pickle: model for taichung city
|   |__ model_XGBR_tainan.pickle: model for tainan city
|   |__ model_XGBR_kaohsiung.pickle: model for kaohsiung city
|
|__ pattern_model
    |__ detect.py: package from rgb-search
    |__ fengshui_detect.py: functions for fengshui-detection
    |__ fengshui_main.py: main execution program
```

<p align="right">(<a href="#top">back to top</a>)</p>


## Quick start

- [Website link](http://34.80.27.2/api)
- [Download model](https://reurl.cc/V1EDo5)

<p align="right">(<a href="#top">back to top</a>)</p>

 
## Acknowledgments

* 房間邊緣偵測參考[rgb-search](https://github.com/rbg-research/Floor-Plan-Detection.git)
* 資料集為台灣政府開放平台取得房屋實價登錄資訊

 <p align="right">(<a href="#top">back to top</a>)</p>