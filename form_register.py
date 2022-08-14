from flask_wtf import FlaskForm
from model import User
from wtforms import StringField, SubmitField, validators, PasswordField,ValidationError
from wtforms.validators import DataRequired, Email

class FormRegister(FlaskForm):
    """依照Model來建置相對應的Form

    password2: 用來確認兩次的密碼輸入相同
    """
    name = StringField('帳號',render_kw={"placeholder": "Enter name"}, validators=[
        validators.DataRequired(),
        validators.Length(3, 30)
    ])
    email = StringField('信箱',render_kw={"placeholder": "Enter email"}, validators=[
        validators.DataRequired(),
        validators.Length(1, 50),
        validators.Email()
    ])
    password = PasswordField('密碼',render_kw={"placeholder": "Enter Password"}, validators=[
        validators.DataRequired(),
        validators.Length(3, 10),
        validators.EqualTo('password2', message='PASSWORD NEED MATCH')
    ])
    password2 = PasswordField('確認密碼',render_kw={"placeholder": "Repeat Password"}, validators=[
        validators.DataRequired()
    ])
    def validate_name(self, field):
        if User.query.filter_by(name=field.data).first():
            raise ValidationError('此帳號已註冊')

    # submit = SubmitField('註冊')
