from app import db

# 定義db模型 (model)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100))

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
    house_age = db.Column(db.Integer)
    gar = db.Column(db.Integer)
    floor = db.Column(db.Integer)
    floor_all = db.Column(db.Integer)
    area = db.Column(db.Numeric(10, 2))
    house_type = db.Column(db.String(30))
    house = db.Column(db.String(30))
    material = db.Column(db.String(30))
    org = db.Column(db.String(30))
    predict_result = db.Column(db.Numeric(10, 2))

    def __init__(self, name, city, region, bedroom, liv, bath, house_age, gar, floor, floor_all, area, house_type, house, material, org, predict_result):
        self.name = name
        self.city = city
        self.region = region
        self.bedroom = bedroom
        self.liv = liv
        self.bath = bath
        self.house_age = house_age
        self.gar = gar
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
            self.house_age,
            self.gar,
            self.floor,
            self.floor_all,
            self.area,
            self.house_type,
            self.house,
            self.material,
            self.org,
            self.predict_result
        )

class Fengshui(db.Model):
    __tablename__ = 'fengshui_result'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)
    fengshui1 = db.Column(db.String(3))
    fengshui2 = db.Column(db.String(3))
    fengshui3 = db.Column(db.String(3))
    images_origin = db.Column(db.String(200))
    images_result = db.Column(db.String(200))

    def __init__(self, name, fengshui1, fengshui2, fengshui3, images_origin, images_result):
            self.name = name,
            self.fengshui1 = fengshui1
            self.fengshui2 = fengshui2
            self.fengshui3 = fengshui3
            self.images_origin = images_origin
            self.images_result = images_result

    def __repr__(self):
        return "User('{}','{}','{}','{}','{}','{}')".format(
            self.name,
            self.fengshui1,
            self.fengshui2,
            self.fengshui3,
            self.images_origin,
            self.images_result
        )
# Base.metadata.create_all(engine)
