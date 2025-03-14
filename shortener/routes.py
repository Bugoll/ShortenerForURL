import qrcode, random, string, os
from shortener import app, db
from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from shortener.forms import RegisterForm, ShortenLinkForm
from werkzeug.security import  check_password_hash

def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_qr_code(short_url):
    img = qrcode.make(short_url)
    img_path = f'static/qrcodes/{short_url}.png'
    os.makedirs(os.path.dirname(img_path), exist_ok=True)
    img.save(img_path)
    return img_path

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home_page():
    form = ShortenLinkForm()
    if form.validate_on_submit():
        long_url = form.destination_link.data
        short_code = generate_short_code()
        qr_code_path = generate_qr_code(short_code)
        conn = db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Link (long) VALUES (?)", (long_url,))
        conn.commit()
        flash('Link shortened successfully!', 'success')
        return redirect(url_for('success'))
    return render_template('home.html', form=form)

@app.route('/success')
def success():
    return "Link shortened successfully!"

@app.route('/personal', methods=['GET', 'POST'])
def personal_page():
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('login_page'))
    conn = db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Link")
    links = cursor.fetchall()
    return render_template('personal.html', links=links)

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        return redirect(url_for('personal_page'))
    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            print(f'There was an error with creating a user: {err_msg}')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = RegisterForm()  # Reusing RegisterForm for simplicity
    if form.validate_on_submit():
        username = form.username.data
        password = form.password1.data
        conn = db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM User WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home_page'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('home_page'))