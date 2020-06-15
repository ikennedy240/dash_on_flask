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
# import function to connect to natrent0
from app.dashapp1.callbacks import psql_connect
import pandas as pd
import os

# path to save user-created data extracts
extract_path = 'extracts/extract.csv'
# set up server to use blueprint
server_bp = Blueprint('main', __name__)

# route for the main page
@server_bp.route('/')
def index():
    return render_template("index.html", title='Home Page')

# route for the login page
@server_bp.route('/login/', methods=['GET', 'POST'])
def login():
    # logged-in users are redirected away
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    # otherwise the get the loginform from forms.py
    form = LoginForm()
    # query the database to make sure the user is valid
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            error = 'Invalid username or password'
            return render_template('login.html', form=form, error=error)

        # then log them in
        login_user(user, remember=form.remember_me.data)
        # this sends them back to the page they were looking for
        next_page = request.args.get('next')
        # and otherwise sends them to the main page
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)

# log out route
@server_bp.route('/logout/')
@login_required
def logout():
    logout_user()

    return redirect(url_for('main.index'))

# registration route
@server_bp.route('/register/', methods=['GET', 'POST'])
def register():
    # logged-in users are redirected away
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    # otherwise the get the RegistrationForm from forms.py
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        # then send the new user to the login page
        return redirect(url_for('main.login'))

    return render_template('register.html', title='Register', form=form)

# route for creatign a data extract
@server_bp.route('/extract/', methods=['GET', 'POST'])
def upload_form():
        # init a natrent connection
        conn = psql_connect()
        c = conn.cursor()
        # grab all the possible listing locs
        c.execute('SELECT DISTINCT listing_loc FROM clean')
        city_call = c.fetchall()
        cities = [(city[0],  city[0]) for city in city_call]

        # use the ExtractSelectionForm from forms.py
        form = ExtractSelectionForm()
        form.city.choices = cities
        # list of possible columns
        cols = ['seq_id','listing_src','listing_loc', 'listing_date', 'listing_title', 'listing_text', 'scraped_neighborhoods', 'scraped_google_maps_url', 'scraped_avail', 'clean_rent', 'clean_beds', 'clean_baths', 'clean_sqft', 'post_origin', 'post_id', 'match_type','x','y','statefp','countyfp','tractce', 'namelsad','geoid']
        if form.validate_on_submit():
            # delete old extract
            if os.path.exists('app/'+extract_path):
                os.remove('app/'+extract_path)

            # modify a base extract call with the user submission
            extract_call = "SELECT {} FROM tract17 JOIN clean ON ST_contains(tract17.geometry, clean.geometry) ".format(','.join(cols))
            extract_call = extract_call+"WHERE listing_loc = '{}' AND listing_date BETWEEN '{}' AND '{}'".format(form.city.data, form.start_date.data, form.end_date.data)

            #read the extract into memory
            df = pd.read_sql(extract_call, conn)
            # let the user know what's going
            flash('Data requested for city {} from {} to {}: found {} rows'.format(
                form.city.data,form.start_date.data, form.end_date.data, df.shape[0]))
            # write their csv to the extract path
            df.to_csv('app/'+extract_path)
            # reload the page to show the extract sample and download button
            return redirect('/extract')
        try:
           df =  pd.read_csv('app/'+extract_path, nrows = 10)
        except:
            df = pd.DataFrame()

        # show the extract sample if available
        print("loaded {} rows, colnames are {}".format(df.shape[0], ', '.join(df.columns.tolist())))
        return render_template('extract.html', cities=cities, form = form, tables=[df.head().to_html(classes='data')], titles=df.columns.values)


# route to serve extract file to user
@server_bp.route('/download')
def download_file():
	path = extract_path
	return send_file(path, as_attachment=True)
