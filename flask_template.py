from collections import namedtuple
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required
import pymysql

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
bootstrap = Bootstrap(app)

class LoginForm(Form):
    email = StringField('Email address', validators=[Required()])
    password = StringField('Password', validators=[Required()])
    submit = SubmitField('Log in')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    if form.validate_on_submit():
        cursor = db.cursor()
        print("form.email.data=" + form.email.data)
        cursor.execute("select customer_id, first_name, last_name " +
                       "from customer where email = %s",
                       (form.email.data,))
        rows = cursor.fetchall()
        if rows:
            print("successful login")
            session['customer_id'] = rows[0][0]
            session['customer_name'] = "{} {}".format(rows[0][1], rows[0][2])
            return redirect(url_for('home'))
        else:
            flash('Email address not found in customer database.')
            return redirect(url_for('index'))
    return render_template('index.html', form=form)

@app.route('/home')
def home():
    cursor = db.cursor()
    cursor.execute(
        "select rental_id, date(rental_date),  " +
        "       date(rental_date + interval film.rental_duration day) as due_date, " +
        "       film.title " +
        "from rental join inventory using(inventory_id) " +
        "            join film using (film_id) "+
        "where customer_id = %s and return_date is null",
        (session['customer_id']))
    Rental = namedtuple('Rental', ['rental_id', 'rental_date',
                                   'due_date', 'film_title'])
    rentals = [Rental._make(row) for row in cursor.fetchall()]
    cursor.close()
    return render_template('home.html', rentals=rentals,
                           customer=session['customer_name'])

@app.route('/usercontrols')
def usercontrols():
    cursor = db.cursor()
    cursor.execute(
        "select last_name, first_name, email from user order by last_name asc")
    rows=cursor.fetchall()
    column_names=[desc[0] for des in cursor.description]
    cursor.close()
    return render_template('ADMINONLYusercontrolpage.html', 
                           columns=column_names, rows=rows)

@app.route('/browse_db')
def browse_db():
    cursor = db.cursor()
    cursor.execute("show tables")
    tables = [field[0] for field in cursor.fetchall()]
    cursor.close()
    return render_template('browse_db.html', dbname=dbname, tables=tables)

@app.route('/table/<table>')
def table(table):
    cursor = db.cursor()
    cursor.execute("select * from " + table)
    rows = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    cursor.close()
    return render_template('table.html', table=table,
                           columns=column_names, rows=rows)

if __name__ == '__main__':
    dbname = 'team3'
    db = pymysql.connect(host='localhost',
                         user='root', passwd='', db=dbname)
    app.run(debug=True)
    db.close()
