# import os
from app import app, db
import os
from form_register import FormRegister
from flask import Flask, render_template, request, redirect, session, url_for, flash
from model import User, Predict, Fengshui
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker, relationship, backref
import price_model.load_model as price_mod
import pattern_model.fengshui_main as pattern_mod


# Route
@app.route('/')
def index():
    return render_template('index.html')

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
        # 檢查帳號和密碼是否正確
        for i in db_session.query(User):
            # 成功登入，在session中記錄會員資訊，導向到會員功能頁面
            if i.name == name and i.password == password:
                url = session.get('url')
                session["name"] = i.name
                if url != None:
                    return redirect(f"/{url}")
                else:
                    return redirect("/")
        # 找不到帳號或密碼，導回登入頁面
        return redirect("/login")

@app.route('/register', methods=["GET", "POST"])
def register():
    # if request.method == 'GET':
    #     return render_template('register.html')
    # else:
    #     # 從前端接收資料
    #     name = request.form["name"]
    #     email = request.form["email"]
    #     password = request.form["psw"]
    form = FormRegister()
    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            email=form.email.data,
            password=form.password.data
        )
        # 建立session
        SqlalchemySession = sessionmaker(bind=db.engine)
        db_session = SqlalchemySession()
        # user = User(name, email, password)
        # 檢查是否有相同帳號
        # for i in db_session.query(User):
        #     if i.name == user.name:
        #         flash("此使用者已經被註冊")
        #         return redirect("/register")
        # 把資料放進資料庫完成註冊
        db_session.add(user)
        db_session.commit()
        flash("註冊成功!")
        return redirect("/login")
    return render_template('register.html', form=form)

@app.route('/pattern')
def pattern_reply():
    # 若已登入直接跳轉至預測頁面
    if "name" in session:
        return render_template('pattern_analysis.html')
    # 尚未登入則記錄網址，登入後跳轉至該預測頁面
    else:
        session['url'] = 'pattern'
        return render_template('pattern.html')

@app.route('/pattern_analysis', methods=['POST'])
def pattern_analysis():
    # 前端取得圖片
    file = request.files['file']
    img_name = file.filename
    # 將圖片存進資料夾
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], img_name))
    file_path_origin='pattern_img/'+img_name
    # 風水判斷
    flag1, flag2, flag3, file_path_result= pattern_mod.pattern_recog(img_name)
    # 輸出結果改為有或無
    if flag1: flag1='有'
    else: flag1='無'
    if flag2: flag2='有'
    else: flag2='無'
    if flag3: flag3='有'
    else: flag3='無'
    # 將結果存進資料庫
    name = session.get('name')
    SqlalchemySession = sessionmaker(bind=db.engine)
    db_session = SqlalchemySession()
    result = Fengshui(name, flag1, flag2, flag3, file_path_origin, file_path_result)
    db_session.add(result)
    db_session.commit()
    # 結果表格表頭
    columns = ["對門相沖", "廳間房大小", "浴廁居中", "原圖", "判斷結果"]
    dicts = {
        '對門相沖':'「對門相沖」<br>常見於現代住宅大樓內，像是大門對大門、大門對陽台門、臥室門對臥室門、臥室門對廁所門、臥室門對廚房門等等，在風水上而言，可能會產生感情不睦、漏財、身體健康受影響等問題。<br>化解方法就是各自在門上掛門帘或者珠簾，阻擋氣場往來。',
        '廳間房大小':'「廳間房大小」<br>通常分為兩種，一為廁所大於廚房，二為房間大於客廳。廁所大於廚房，在風水上而言，可能會產生胃腸出現毛病，身體虛弱、晚得子嗣的狀況。<br>房間大於客廳，在風水上而言，可能會有家人間關係疏離，朋友貴人減少、前途受到阻礙的狀況。<br>化解方法：若房間大於客廳的情形，可以在房間內增加隔間，使房間面積變小；若為廁所大於廚房，則無法化解，必須在事先規劃就須將格局想好。',
        '浴廁居中':'「浴廁居中」<br>住宅的中心點為家運旺衰的主要關鍵位置，可以為客廳、書房、臥室但絕對不可以為廁所，在風水上而言，可能會有身體健康受影響、家運受壓無法發展、讀書不利、考運不吉、財運不佳的問題。<br>化解方法：在廁所內擺上黃金葛、投射燈，來淨化穢氣活化氣場，並在門口掛上長布簾來阻絕穢氣外泄。',
        }

    # 從資料庫抓歷史紀錄
    SqlalchemySession = sessionmaker(bind=db.engine)
    db_session = SqlalchemySession()
    img_history = db_session.query(Fengshui).filter_by(name=name).order_by(Fengshui.id.desc())
    return render_template('pattern_result.html',
                            file_path_origin=file_path_origin,
                            file_path_result=file_path_result,
                            flag1=flag1,
                            flag2=flag2,
                            flag3=flag3,
                            dicts=dicts,
                            columns=columns,
                            img_history=img_history)

@app.route('/predict')
def predict_reply():
    # 若已登入直接跳轉至預測頁面
    if "name" in session:
        return render_template('predict_analysis.html')
    # 尚未登入則記錄網址，登入後跳轉至該預測頁面
    else:
        session['url'] = 'predict'
        return render_template('predict.html')

@app.route('/predict_analysis', methods=['GET', 'POST'])
def predict_analysis():
    # 從前端取得輸入條件
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
    house = request.form['house']
    material = request.form['material']
    org = request.form['org']
    # 開始預測
    predict_result = price_mod.price_predict(
        city, region, bedroom, liv, bath, gar_price, house_age, floor, floor_all, area, house_type, house, material, org)
    # 建立session
    SqlalchemySession = sessionmaker(bind=db.engine)
    db_session = SqlalchemySession()
    # 將預測結果存入資料庫
    predict = Predict(name, city, region, bedroom, liv, bath, gar_price, house_age,
                      floor, floor_all, area, house_type, house, material, org, predict_result[0])
    db_session.add(predict)
    db_session.commit()
    return redirect('/predict_result')

@app.route("/predict_result")
def predict_result():
    # 從資料庫抓歷史紀錄
    columns = ['預測地點', '鄉鎮市區', '房間數量', '廳間數量', '衛浴數量', '屋齡', '建物坪數', 
               '車位數量','居住樓層', '總樓層數', '交易標的', '建物型態', '主要建材', '有無管理組織', '預測結果']
    # 建立session
    SqlalchemySession = sessionmaker(bind=db.engine)
    db_session = SqlalchemySession()
    # 依照id排列順序
    predict_options = db_session.query(Predict).filter_by(
        name=session.get("name")).order_by(Predict.id.desc())
    # 取出最新的預測結果
    predict_result = predict_options.first().predict_result
    return render_template('predict_result.html',
                            columns=columns,
                            predict_options=predict_options,
                            predict_result=predict_result)

@app.route('/mortgate_calculator')
def mortgate_calculator():
    return render_template('mortgage.html')

@app.route('/affordable_calculator')
def affordable_calculator():
    return render_template('affordable.html')

# 登出
@app.route("/signout")
def signout():
    session.pop("name", None)
    session.pop("url", None)
    return redirect("/")

# 啟動伺服器
if __name__ == '__main__':
    app.run()
