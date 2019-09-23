from datetime import datetime

import ldap3

from functools import wraps

from flask import request, render_template, flash, redirect, url_for, Blueprint, g
from flask_login import current_user, login_user, logout_user, login_required

from app.extensions import login_manager, db
from app.auth.models import User, LoginForm


auth = Blueprint('auth', __name__)


def requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.has_role(roles):
                # Redirect the user to an unauthorized notice!
                flash('You need to be an admin to view this page.')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return wrapped
    return wrapper


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@auth.before_request
def get_current_user():
    g.user = current_user


@auth.route('/')
@auth.route('/home')
def home():
    return render_template('home.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged in.')
        return redirect(url_for('auth.home'))

    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        #username = request.form.get('username')
        #password = request.form.get('password')
        username = form.username.data
        password = form.password.data

        # Check whether user is local or directory.
        # Note that the user must exist in the database.

        user = User.query.filter_by(username=username).first()

        if not user:
            flash('User has not been created. Please request access from the administrator.')
            return render_template('login.html', form=form)

        if user.local_user:
            # Authenticate against password stored in database.

            if not user.check_password(password):
                flash('Invalid username or password. Please try again.', 'danger')
                return render_template('login.html', form=form)

        else:
            # Authenticate aginst LDAP.
            try:
                User.try_login(username, password)
            except ldap3.core.exceptions.LDAPInvalidCredentialsResult:
                flash('Invalid username or password. Please try again.', 'danger')
                return render_template('login.html', form=form)

        #if not user:
        #    user = User(username=username, password=password)
        #    db.session.add(user)
        #    db.session.commit()

        login_user(user)

        user.last_login_at = user.current_login_at
        user.current_login_at = datetime.utcnow()
        user.last_login_ip = user.current_login_ip
        user.current_login_ip = request.remote_addr or None
        user.login_count = user.login_count + 1 if user.login_count else 1
        db.session.commit()

        flash('You have successfully logged in.', 'success')
        return redirect(url_for('main.home'))

    if form.errors:
        flash(form.errors, 'danger')

    return render_template('login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.home'))
