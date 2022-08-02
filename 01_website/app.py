import os
import price_model.load_model as model
from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DECIMAL
from flask_migrate import Migrate
from sqlalchemy.orm import sessionmaker, relationship, backref
UPLOAD_FOLDER = './static/img'

# 建立Application物件靜態檔案處理設定
app = Flask(__name__,
            static_folder="static",
            static_url_path="/"
            )
# 設定session的密鑰
app.secret_key = 'super secret key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SESSION_PERMANENT"] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
# app.config['PERMANENT_SESSION_LIFETIME'] = False

# 資料庫設定
postgresql_database_uri='postgresql://xopuyyzemzluai:4fff306079be0f629d7074ea8794119aec4cefbe5cc18922be2360880e87eb85@ec2-3-213-228-206.compute-1.amazonaws.com:5432/d5gno1favbhc32'
mysql__database_uri='mysql+pymysql://root:123456@localhost:3306/our_users'
app.config['SQLALCHEMY_TRACK_MODFICATIONS']=False
app.config['SQLALCHEMY_DATABASE_URI'] = mysql__database_uri
# app.config['SQLALCHEMY_DATABASE_URI']=postgresql_database_uri
db = SQLAlchemy(app)

# engine = create_engine(postgresql_database_uri, echo=True)
engine = create_engine(mysql__database_uri, echo=True)

# 建立描述資料庫表格的類別
# Base = declarative_base()

# migrate 紀錄更新資料庫
migrate = Migrate(app, db)

# 定義db模型 (model)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(String(100))

    # rel_user_predict = relationship("Predict", backref=backref("test_table"))

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

    def __repr__(self):
        return "User('{}','{}', '{}')".format(
            self.name,
            self.email,
            self.password
        )


class Predict(db.Model):
    __tablename__ = 'price_result'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30))
    city = db.Column(db.String(50))
    region = db.Column(db.String(50))
    bedroom = db.Column(db.Integer)
    liv = db.Column(db.Integer)
    bath = db.Column(db.Integer)
    gar_price = db.Column(db.Integer)
    house_age = db.Column(db.Integer)
    floor = db.Column(db.Integer)
    floor_all = db.Column(db.Integer)
    area = db.Column(db.Numeric(10,2))
    house_type = db.Column(db.String(30))
    house = db.Column(db.String(30))
    material = db.Column(db.String(30))
    org = db.Column(db.String(30))
    predict_result = db.Column(db.Numeric(10,2))

    def __init__(self, name, city, region, bedroom, liv,bath, gar_price, house_age, floor, floor_all, area, house_type,house, material, org, predict_result):
        self.name = name
        self.city = city
        self.region = region
        self.bedroom = bedroom
        self.liv = liv
        self.bath = bath
        self.gar_price = gar_price
        self.house_age = house_age
        self.floor = floor
        self.floor_all = floor_all
        self.area = area
        self.house_type = house_type
        self.house = house
        self.material = material
        self.org = org
        self.predict_result = predict_result

    def __repr__(self):
        return "Predict('{}','{}','{}', '{}','{}','{}', '{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(
            self.name,
            self.city,
            self.region,
            self.bedroom,
            self.liv,
            self.bath,
            self.gar_price,
            self.house_age,
            self.floor,
            self.floor_all,
            self.area,
            self.house_type,
            self.house,
            self.material,
            self.org,
            self.predict_result
        )


# Base.metadata.create_all(engine)

# Route
@app.route('/')
def index():
    return render_template('index.html')

# @app.route('/base')
# def base_test():
#     return render_template('base.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/info')
def info():
    return render_template('info.html')


@app.route('/mortgage')
def mortgage():
    return render_template('mortgage.html')


@app.route('/affordable')
def affordable():
    return render_template('affordable.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        # 從前端取得使用者的輸入
        name = request.form["name"]
        password = request.form["psw"]
        # 建立session
        SqlalchemySession = sessionmaker(bind=db.engine)
        db_session = SqlalchemySession()
        # 檢查信箱和密碼是否正確
        for i in db_session.query(User):
            # 成功登入，在session中記錄會員資訊，導向到會員頁面
            if i.name == name and i.password == password:
                url = session.get('url')
                session["name"] = i.name
                if url != None:
                    return redirect(f"/{url}")
                else:
                    return redirect("/")
        # 找不到信箱或密碼，導向錯誤頁面
        return redirect("/login")


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        # 從前端接收資料
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["psw"]
        # 建立session
        SqlalchemySession = sessionmaker(bind=db.engine)
        db_session = SqlalchemySession()
        user = User(name, email, password)
        # 檢查是否有相同email的文件資料
        for i in db_session.query(User):
            if i.email == email:
                flash("信箱已經被註冊")
                return redirect("/register")
        # 把資料放進資料庫完成註冊
        db_session.add(user)
        db_session.commit()
        flash("註冊成功!")
        return redirect("/login")


@app.route('/pattern')
def pattern_reply():
    if "name" in session:
        return render_template('pattern_analysis.html')
    else:
        session['url'] = 'pattern'
        return render_template('pattern.html')


# @app.route('/pattern_analysis', methods=['POST'])
# def pattern_analysis():
#     city = request.form


@app.route('/predict')
def predict_reply():
    if "name" in session:
        return render_template('predict_analysis.html')
    else:
        session['url'] = 'predict'
        return render_template('predict.html')


@app.route('/predict_analysis', methods=['GET', 'POST'])
def predict_analysis():
    name = session.get('name')
    city = request.form['city']
    region = request.form['region']
    bedroom = request.form['bedroom']
    liv = request.form['liv']
    bath = request.form['bath']
    gar_price = request.form['gar_price']
    house_age = request.form['house_age']
    floor = request.form['floor']
    floor_all = request.form['floor_all']
    area = request.form['area']
    house_type = request.form['house_type']
    house=request.form['house']
    material = request.form['material']
    org = request.form['org']
    predict_result=model.price_predict(city, region, bedroom, liv, bath, gar_price,house_age, floor, floor_all, area, house_type, house, material, org)
    # 建立session
    SqlalchemySession = sessionmaker(bind=db.engine)
    db_session = SqlalchemySession()
    predict = Predict(name, city, region, bedroom, liv, bath, gar_price,house_age, floor, floor_all, area, house_type, house, material, org, predict_result[0])
    db_session.add(predict)
    db_session.commit()
    return redirect('/predict_result')

@app.route("/predict_result")
def predict_result():
    columns=['預測地點', '鄉鎮市區', '房間數量', '廳間數量', '衛浴數量', '車位總價','屋齡', '移轉層次', '總樓層數',
       '建物坪數', '交易標的', '建物型態', '主要建材', '有無管理組織','預測結果']
    # 建立session
    SqlalchemySession = sessionmaker(bind=engine)
    db_session = SqlalchemySession()
    predict_options = db_session.query(Predict).filter_by(name=session.get("name")).order_by(Predict.id.desc())
    predict_result = predict_options.first().predict_result
    return render_template('predict_result.html',columns=columns,predict_options=predict_options,predict_result=predict_result)


@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files["file"]
        if file.filename != '':
            file.save(os.path.join(UPLOAD_FOLDER, file.filename))
            return redirect(url_for('pattern'))


@app.route('/mortgate_calculator')
def mortgate_calculator():
    return render_template('mortgage.html')


@app.route('/affordable_calculator')
def affordable_calculator():
    return render_template('affordable.html')


@app.route("/signout")
def signout():
    session.pop("name", None)
    session.pop("url", None)
    return redirect("/")


# 啟動伺服器
if __name__ == '__main__':
    app.run(debug=True)
