from wtforms import StringField, Form, PasswordField
from wtforms.validators import DataRequired, Length


class TaskForm(Form):
    task = StringField(validators=[DataRequired(), Length(min=1, max=30)], render_kw={'autofocus': True})


class UserForm(Form):
    login = StringField(validators=[DataRequired(), Length(min=4, max=15)], render_kw={'autofocus': True})
    password = PasswordField(validators=[DataRequired(), Length(min=4, max=20)])
