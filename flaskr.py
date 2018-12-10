import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing

DATABASE = 'flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.before_request
def before_request():
    g.db = connect_db()


@app.after_request
def after_request(response):
    g.db.close()
    return response


@app.route('/show_entries')
def show_entries():
    cur = g.db.execute('select title, text, id from entries order by id desc')
    entries = [dict(title=row[0], text=row[1], id=row[2]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


@app.route('/')
def index():
    cur = g.db.execute('select title, text, id from entries order by id desc')
    entries = [dict(title=row[0], text=row[1], id=row[2]) for row in cur.fetchall()]
    return render_template('index.html', entries=entries)


@app.route('/show_detail/<int:title_id>')
def show_detail(title_id):
    cur = g.db.execute('select title, text, id from entries where id = ' + str(title_id))
    entries = [dict(title=row[0], text=row[1], id=row[2]) for row in cur.fetchall()]
    return render_template('show_detail.html', entries=entries)


if __name__ == '__main__':
    app.run()
