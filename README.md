# BDSE25 Team1 project 家圖四必

### Outline

- [About](#about)
- [Demo](#demo)
- [Usage](#usage)
- [Contents](#contents)
- [Web Architecture](#web-architecture)
- [Quick start](#quick-start)



## About

[簡介專題構想、前言]  
台灣房價逐年攀升，買第一間房的平均年齡上升至35-40歲，還完30年房貸年齡已近70，換房的可能性相對降低許多；在房價維持在如此高檔的情況下，發現風水上的瑕疵很難有能力換屋，但在台灣有60%的人買房重視風水。因此，若能透過歷年房價分析房價趨勢搭配格局圖的風水檢測，更能讓一般市井小名買得安心，住的放心。

<p align="right">(<a href="#top">back to top</a>)</p>



## Demo

[苡晏影片]  
![Demo image]("/01_website/static/img/testimonial-2.jpg")


<p align="right">(<a href="#top">back to top</a>)</p>



## Usage

[用途] 

* 預測台灣直轄市房屋價格
* 檢視台灣歷年房價
* 提供貸款能力試算
* 判斷格局圖風水問題


<p align="right">(<a href="#top">back to top</a>)</p>



## Contents

[內容說明]

* 房價預測 (based on Hadoop cluster)
    * 資料清洗
    * 特徵工程
    * 模型訓練
    
* 歷年房價資訊
    * 資料處理與視覺化

* 格局圖影像辨識
    * 房間邊緣辨識
    * 文字OCR偵測
    * 風水判斷

* 會員登入系統
    * 基礎會員CRUD功能


<p align="right">(<a href="#top">back to top</a>)</p>




## Web Architecture
```
|__ app.py: create all route
|__ config.py: set all config
|__ requirements.txt: all python package requirements
|__ bdse25
    |__ __init__.py: 初始化
    |__ models.py: 連接使用者資料庫
    |__ webforms.py: 註冊、登入表格設定
    |__ example.py: ...
        ...
            ...
                ...
```

<p align="right">(<a href="#top">back to top</a>)</p>


## Quick start
- [Website link](#)
- [Download model](https://reurl.cc/V1EDo5)
- Install site-packages  
    ```bash
    pip install -r requirements.txt
    ```

<p align="right">(<a href="#top">back to top</a>)</p>

 
## Acknowledgments
* 房間邊緣偵測參考rgb-search與及使用```FloorplanToBlenderLib```套件<br>
link: https://github.com/rbg-research/Floor-Plan-Detection.git

* 資料集為台灣政府開放平台取得房屋實價登錄資訊

 <p align="right">(<a href="#top">back to top</a>)</p>