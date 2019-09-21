import pytz

from ldap3 import Server, Connection, ALL
from werkzeug.security import generate_password_hash, check_password_hash

from flask_wtf import FlaskForm
from flask_login import AnonymousUserMixin
from flask_login import UserMixin as BaseUserMixin
from wtforms import TextField, PasswordField
from wtforms.validators import InputRequired

from flask import current_app as app
from app.extensions import db

roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class RoleMixin(object):
    """Mixin for `Role` model definitions"""

    def __eq__(self, other):
        return (self.name == other or
                self.name == getattr(other, 'name', None))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.name)


class AnonymousUser(AnonymousUserMixin):
    """AnonymousUser definition with role"""
    def __init__(self):
        self.roles = []

    def has_role(self, *args):
        return False


class UserMixin(BaseUserMixin):
    """Mixin for `User` model definitions"""

    @property
    def is_active(self):
        """Returns `True` if the user is active."""
        return self.active

    def get_auth_token(self):
        """Returns the user's authentication token."""
        data = [str(self.id), hash_data(self.password)]
        return _security.remember_token_serializer.dumps(data)

    def has_role(self, role):
        """Returns `True` if the user identifies with the specified role.
        :param role: A role name or `Role` instance"""
        if isinstance(role, string_types):
            return role in (role.name for role in self.roles)
        else:
            return role in self.roles

    def get_security_payload(self):
        """Serialize user object as response payload."""
        return {'id': str(self.id)}

    def verify_and_update_password(self, password):
        """Verify and update user password using configured hash."""
        return verify_and_update_password(password, self)


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))

    email = db.Column(db.String(255), unique=True)
    name = db.Column(db.String(255))

    password_hash = db.Column(db.String(255))
    active = db.Column(db.Boolean(), default=True)
    local_user = db.Column(db.Boolean(), default=True)
    roles = db.relationship('Role',
                            secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(32))
    current_login_ip = db.Column(db.String(32))
    login_count = db.Column(db.Integer())
    timezone = db.Column(db.String(64))


    @staticmethod
    def try_login(username, password):
        """Attempt to authenticate against LDAP"""
        server = Server(app.config['LDAP_HOST'], port=app.config['LDAP_PORT'], get_info=ALL)

        conn = Connection(server,
                          user="{}={},{},{}".format(app.config['LDAP_USER_ATTR'],
                                                    username,
                                                    app.config['LDAP_USER_DN'],
                                                    app.config['LDAP_BASE_DN']),
                          password=password,
                          raise_exceptions=True)
        print(conn)
        conn.bind()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_tz(self):
        if self.timezone:
            return pytz.timezone(self.timezone)
        else:
            return app.config.get("DEFAULT_TIMEZONE", pytz.utc)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def has_role(self, role):
        return role in self.roles


class LoginForm(FlaskForm):
    username = TextField('Username', [InputRequired()])
    password = PasswordField('Password', [InputRequired()])
