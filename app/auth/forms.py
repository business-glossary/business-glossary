#   Copyright 2017 Alan Tindale, All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import InputRequired, Email, EqualTo
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from flask_admin.form.widgets import Select2Widget

from app.auth.models import User, Role

class LocalUserForm(FlaskForm):
    """Form to add a local database user"""
    name = StringField('Name', validators=[InputRequired()])
    username = StringField('User Name', validators=[InputRequired()])
    email = StringField('Email Address', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    password2 = PasswordField('Repeat Password', validators=[InputRequired(), EqualTo('password')])
    roles = QuerySelectField(query_factory=lambda: Role.query.all(),
                             get_label="name",
                             allow_blank=True,
                             widget=Select2Widget())
    submit = SubmitField('Submit')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class DirectoryUserForm(FlaskForm):
    """Form to add a directory user"""
    name = StringField('Name', validators=[InputRequired()])
    username = StringField('User Name', validators=[InputRequired()])
    roles = QuerySelectField(query_factory=lambda: Role.query.all(),
                             get_label="name",
                             allow_blank=True,
                             widget=Select2Widget())
    submit = SubmitField('Submit')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
