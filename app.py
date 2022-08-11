# import os
# from PIL import Image
from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DECIMAL,UnicodeText,Integer,LargeBinary
from flask_migrate import Migrate
from sqlalchemy.orm import sessionmaker, relationship, backref
from flask_bootstrap import Bootstrap
import easyocr

UPLOAD_FOLDER = './static/pattern_img'
EASYOCR_READER = easyocr.Reader(['ch_tra','en']) 

# 建立Application物件靜態檔案處理設定
app = Flask(__name__,
            static_folder="static",
            static_url_path="/bdse25_team1"
            )


# 設定session的密鑰
app.secret_key = 'super secret key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SESSION_PERMANENT"] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
# app.config['PERMANENT_SESSION_LIFETIME'] = False

# 資料庫設定
mysql_database_uri = 'mysql+pymysql://root:546213@localhost:3306/accounts'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = mysql_database_uri
db = SQLAlchemy(app)

engine = create_engine(mysql_database_uri, echo=True)

# 建立描述資料庫表格的類別
# Base = declarative_base()

# migrate 紀錄更新資料庫
migrate = Migrate(app, db)
bootstrap = Bootstrap(app)
