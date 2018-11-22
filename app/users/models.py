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

import pytz

from flask_security import Security, RoleMixin, UserMixin
from flask_sqlalchemy import SQLAlchemy

from app.extensions import db

# Define models
roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    name = db.Column(db.String(255))

    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    confirmed_at = db.Column(db.DateTime())
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(32))
    current_login_ip = db.Column(db.String(32))
    login_count = db.Column(db.Integer())
    timezone = db.Column(db.String(64))

    def get_tz(self):
        if self.timezone:
            return pytz.timezone(self.timezone)
        else:
            return app.config.get("DEFAULT_TIMEZONE", pytz.utc)

    def has_role(self, role):
            return role in self.roles

    def dict(self):
        """
        A dictionary representation that can be used for JSON serialization
        """
        return {
            "email": self.email,
            "active": self.active,
            "confirmed_at": api.serialize_date(self.confirmed_at),
            "timezone": self.timezone
        }

    def __str__(self):
        return self.name or self.email
