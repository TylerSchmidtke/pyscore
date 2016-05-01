from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user, logout_user
from flask.ext.bcrypt import generate_password_hash
from . import auth
from .forms import RegisterForm, LoginForm
from ..models import User


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(displayname=form.username.data.rstrip(),
                    username=form.username.data.lower().rstrip(),
                    password_hash=generate_password_hash(form.password.data, rounds=15),
                    registration_ip=request.remote_addr)
        user.save()
        flash('You can now login!')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(username=form.username.data.lower().rstrip()).first()
        if user is not None and user.verify_password(form.password.data.rstrip()):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))