from uuid import uuid4

from flask import Blueprint, render_template, request, flash, redirect, url_for
from website.models import User
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,login_required, logout_user, current_user


auth = Blueprint('auth', __name__)

'''
API call to login
'''


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        check_user = User.objects(email_id=email).first()
        if check_user:
            if check_password_hash(check_user.password, password):
                flash("Logged in successfully", category="success")
                login_user(check_user, remember=True)
                return render_template("home.html", user=current_user)
            else:
                flash("incorrect password", category="error")
        else:
            flash("email id doesn't exist!", category="error")
    return render_template("login.html", user=current_user)


'''
API call for logout
'''


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template("login.html", user=current_user)


'''
API call for sign up
'''


@auth.route('/sign-up', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        check_user = User.objects(email_id=email).first()
        if check_user:
            flash("User already exists!", category="error")
        elif len(email) < 4:
            flash('email must be greater than 4 characters', category="error")
        elif len(firstname) < 2:
            flash('first name should be greater than 2 characters', category="error")
        elif len(password1) < 7:
            flash('password must be at least 7 characters', category="error")
        elif password2 != password1:
            flash("password doesn't match", category="error")

        else:
            create_user = User.create(id=uuid4(), email_id=email, first_name=firstname, last_name=lastname, password=generate_password_hash(password1, method='sha256'))
            create_user.save()
            flash('Account created!', category="success")
            login_user(create_user, remember=True)
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)


