from wtforms import Form, StringField
from wtforms.validators import DataRequired, Length


class TaskForm(Form):
    task = StringField(validators=[DataRequired(), Length(min=1, max=30)], render_kw={'autofocus': True})
