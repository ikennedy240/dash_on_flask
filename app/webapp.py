from flask import Blueprint
from flask import redirect, flash
from flask import render_template
from flask import request
from flask import url_for
from flask import send_file
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user
from werkzeug.urls import url_parse

from app.extensions import db
from app.forms import LoginForm
from app.forms import RegistrationForm, ExtractSelectionForm
from app.models import User
from app.dashapp1.callbacks import psql_connect
import pandas as pd
import os

extract_path = 'extracts/extract.csv'
server_bp = Blueprint('main', __name__)


@server_bp.route('/')
def index():
    return render_template("index.html", title='Home Page')


@server_bp.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            error = 'Invalid username or password'
            return render_template('login.html', form=form, error=error)

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)


@server_bp.route('/logout/')
@login_required
def logout():
    logout_user()

    return redirect(url_for('main.index'))


@server_bp.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('main.login'))

    return render_template('register.html', title='Register', form=form)

@server_bp.route('/extract/', methods=['GET', 'POST'])
def upload_form():
        conn = psql_connect()
        c = conn.cursor()
        c.execute('SELECT DISTINCT listing_loc FROM clean')
        city_call = c.fetchall()
        cities = [(city[0],  city[0]) for city in city_call]
        form = ExtractSelectionForm()
        form.city.choices = cities
        if form.validate_on_submit():
            # delete old extract
            if os.path.exists('app/'+extract_path):
                os.remove('app/'+extract_path)
            flash('Data requested for city {}'.format(
                form.city.data))
            extract_call = "SELECT * FROM clean WHERE listing_loc = '{}' AND listing_date BETWEEN NOW() - INTERVAL '7 DAYS' AND NOW()".format(form.city.data)
            df = pd.read_sql(extract_call, conn)
            print(os.getcwd())
            df.to_csv('app/'+extract_path)
            return redirect('/extract')
        return render_template('extract.html', cities=cities, form = form)

@server_bp.route('/download')
def download_file():
	path = extract_path
	return send_file(path, as_attachment=True)
